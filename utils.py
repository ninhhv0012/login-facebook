# Các hàm tiện ích (Utility functions)
from datetime import datetime
import os
import base64
from nacl.public import PublicKey, SealedBox
from Crypto.Cipher import AES

# Đường dẫn thư mục lưu cookies
folder_path = "cookies"

def get_cookies_string(session):
    """Chuyển đổi cookies của session thành định dạng chuỗi"""
    """Convert session cookies to string format"""
    cookies = []
    for cookie in session.cookies:
        cookies.append(f"{cookie.name}={cookie.value}")
    return "; ".join(cookies)

def save_to_file(email, password, two_fa_code, cookies):
    """Lưu thông tin tài khoản vào file"""
    """Save account information to file"""
    try:
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(folder_path, exist_ok=True)
        # Tạo tên file với timestamp
        date_time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_name = f"{folder_path}/account_{date_time}.txt"
        
        # Ghi thông tin vào file
        with open(file_name, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            line = f"{email}|{password}|{two_fa_code}|{cookies}|{timestamp}\n"
            f.write(line)
        return True, file_name
    except Exception as e:
        print(f"Lỗi khi lưu file: {str(e)}")  # Error saving to file
        return False, None
    
def fb_encrypt_password(pub_key_hex: str,
                        key_id: int,
                        password: str,
                        timestamp: str,
                        enc_prefix: str = "#PWD_BROWSER",
                        version: int = 5) -> str:
    """
    Trả về chuỗi mã hóa giống hệt format của Facebook:
        #PWD_BROWSER:5:<timestamp>:<base64_envelope>
    """

    # 1. Chuẩn bị public key và encrypt sym_key với sealed box
    pub_key = PublicKey(bytes.fromhex(pub_key_hex))
    sealed_box = SealedBox(pub_key)
    sym_key = os.urandom(32)                # AES-256 key ngẫu nhiên
    sealed_key = sealed_box.encrypt(sym_key)  # sealed_box.encrypt trả về Uint8Array sealed key :contentReference[oaicite:0]{index=0}

    # 2. AES-GCM encrypt password, dùng IV = 12 byte 0 và timestamp làm AAD
    iv = b"\x00" * 12
    cipher = AES.new(sym_key, AES.MODE_GCM, nonce=iv, mac_len=16)
    cipher.update(timestamp.encode("utf-8"))          # additionalData = timestampUTF8 :contentReference[oaicite:1]{index=1}
    ciphertext, tag = cipher.encrypt_and_digest(password.encode("utf-8"))

    # 3. Ghép envelope: [versionByte][keyIdByte][sealedKeyLen(2 bytes LE)] 
    #                   + sealedKey + tag + ciphertext
    envelope = (
        (1).to_bytes(1, "little") +                  # internal envelope version = 1
        (key_id & 0xFF).to_bytes(1, "little") +      # keyId (1 byte)
        len(sealed_key).to_bytes(2, "little") +      # sealedKey length (2 bytes little-endian)
        sealed_key +                                 # sealed symmetric key
        tag +                                        # AES-GCM tag (16 bytes)
        ciphertext                                   # AES-GCM cipher text
    )

    # 4. Base64-encode và format ra string cuối cùng
    b64_env = base64.b64encode(envelope).decode("ascii")
    return f"{enc_prefix}:{version}:{timestamp}:{b64_env}"
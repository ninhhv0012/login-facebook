# Các hàm tiện ích (Utility functions)
from datetime import datetime
import os

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
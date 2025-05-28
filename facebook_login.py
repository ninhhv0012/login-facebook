import requests
import re
import time
import json
import base64
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse
from utils import get_cookies_string
import random

class FacebookLogin:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Cấu hình session với hành vi trình duyệt thực tế"""
        # Sử dụng User-Agent giống trình duyệt thật
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
    
    def simulate_real_browsing(self):
        """Mô phỏng hành vi duyệt web thực tế trước khi đăng nhập"""
        try:
            print("🌐 Đang mô phỏng hành vi duyệt web thực tế...")
            
            # Bước 1: Truy cập trang chính trước
            time.sleep(random.uniform(1, 3))
            main_response = self.session.get('https://www.facebook.com/', timeout=15)
            print(f"✅ Đã tải trang chính: {main_response.status_code}")
            
            # Bước 2: Mô phỏng độ trễ và hành động ngẫu nhiên
            time.sleep(random.uniform(2, 4))
            
            # Bước 3: Tải trang đăng nhập với trường Referer phù hợp
            self.session.headers.update({
                'Referer': 'https://www.facebook.com/'
            })
            
            login_response = self.session.get('https://www.facebook.com/login/', timeout=15)
            print(f"✅ Đã tải trang đăng nhập: {login_response.status_code}")
            
            return login_response.text, 'https://www.facebook.com/login/'
            
        except Exception as e:
            print(f"❌ Mô phỏng duyệt web thất bại: {str(e)}")
            # Fallback to direct login page access
            return self.get_login_page_direct()
    
    def get_login_page_direct(self):
        """Truy cập trực tiếp trang đăng nhập (dự phòng)"""
        try:
            response = self.session.get('https://www.facebook.com/', timeout=15)
            return response.text, 'https://www.facebook.com/'
        except Exception as e:
            raise Exception(f"Lỗi khi load trang: {str(e)}")
    
    def extract_comprehensive_form_data(self, html_content):
        """Trích xuất dữ liệu form một cách toàn diện với nhiều kỹ thuật"""
        soup = BeautifulSoup(html_content, 'html.parser')
        form_data = {}
        
        print("🔍 Bắt đầu trích xuất dữ liệu form...")
        
        # Phương pháp 1: Tìm chính xác form đăng nhập
        login_forms = []
        
        # Thử nhiều bộ chọn khác nhau
        selectors = [
            {'data-testid': 'royal_login_form'},
            {'id': 'login_form'},
            {'action': re.compile(r'login')},
        ]
        
        for selector in selectors:
            forms = soup.find_all('form', selector)
            if forms:
                login_forms.extend(forms)
                print(f"✅ Found {len(forms)} form(s) with selector: {selector}")
        
        # Nếu không tìm thấy form đăng nhập cụ thể, sử dụng tất cả các form
        if not login_forms:
            login_forms = soup.find_all('form')
            print(f"⚠️ Không tìm thấy form đăng nhập cụ thể, sử dụng {len(login_forms)} form(s) tổng quát")
        
        # Trích xuất dữ liệu từ các form đăng nhập
        for i, form in enumerate(login_forms):
            # In thông tin về form hiện tại đang được xử lý
            print(f"🔍 Đang trích xuất từ form {i+1}:")
            for inp in form.find_all('input'):
                name = inp.get('name')
                value = inp.get('value', '')
                input_type = inp.get('type', 'text')
                
                if name:
                    # Chỉ lấy các trường cần thiết
                    if name not in ['email', 'pass']:
                        form_data[name] = value
                        print(f"   📝 {name} = {value[:30]}... (type: {input_type})")
        
        # Phương pháp 2: Sử dụng regex để trích xuất các token quan trọng
        token_patterns = {
            'lsd': [
                r'name="lsd"\s+value="([^"]+)"',
                r'"LSD"[^}]*"token":"([^"]+)"',
                r'"lsd":"([^"]+)"',
                r'LSD[^,]*,\s*\[\],\s*\{\s*"token"\s*:\s*"([^"]+)"'
            ],
            'jazoest': [
                r'name="jazoest"\s+value="([^"]+)"',
                r'"jazoest":"([^"]+)"',
                r'jazoest[^"]*"([^"]+)"'
            ],
            'fb_dtsg': [
                r'name="fb_dtsg"\s+value="([^"]+)"',
                r'"DTSGInitialData"[^}]*"token":"([^"]+)"',
                r'"fb_dtsg":"([^"]+)"',
                r'DTSGInitialData[^}]*token[^"]*"([^"]+)"'
            ],
            'datr': [
                r'"_js_datr","([^"]+)"',
                r'datr[^"]*"([^"]+)"'
            ]
        }
        
        print("🔍 Đang trích xuất token bằng regex patterns:")
        for token_name, patterns in token_patterns.items():
            if token_name not in form_data:
                for pattern in patterns:
                    matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
                    if matches:
                        # Lấy giá trị đầu tiên không rỗng
                        value = next((m for m in matches if m.strip()), None)
                        if value:
                            # Loại bỏ ký tự không cần thiết
                            value = value.replace('\\', '').replace('&amp;', '&').strip()
                            form_data[token_name] = value
                            print(f"   ✅ {token_name}: {value[:30]}...")
                            break
                
                if token_name not in form_data:
                    print(f"   ❌ {token_name}: NOT FOUND")
        
        # Phương pháp 3: Trích xuất các trường bổ sung từ HTML
        additional_fields = {
            'privacy_mutation_token': r'privacy_mutation_token=([^&"]+)',
            'next': r'name="next"\s+value="([^"]*)"',
            'login_source': r'name="login_source"\s+value="([^"]*)"',
            'shared_prefs_data': r'name="shared_prefs_data"\s+value="([^"]*)"'
        }
        
        print("🔍 Trích xuất các trường bổ sung:")
        for field_name, pattern in additional_fields.items():
            if field_name not in form_data:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    form_data[field_name] = match.group(1)
                    print(f"   ✅ {field_name}: {match.group(1)[:30]}...")
        
        # Phương pháp 4: Thêm các giá trị mặc định nếu không có
        defaults = {
            'login_source': 'comet_headerless_login',
            'next': '',
            'shared_prefs_data': ''
        }
        
        for key, value in defaults.items():
            if key not in form_data:
                form_data[key] = value
                print(f"   📝 Mặc định {key}: {value}")
        
        print(f"✅ Tổng số trường đã trích xuất: {len(form_data)}")
        
        # Xác thực các trường quan trọng
        critical_fields = ['lsd']  # Tối thiểu chúng ta cần lsd
        missing_critical = [field for field in critical_fields if field not in form_data]
        
        if missing_critical:
            print(f"❌ Thiếu các trường quan trọng: {missing_critical}")
            return None
        
        return form_data
    
    def login(self, email, password, two_fa_code=None):
        """Đăng nhập Facebook nâng cao với khả năng tránh phát hiện bot tốt hơn"""
        try:
            print("🚀 Bắt đầu quá trình đăng nhập Facebook...")
            
            # Bước 1: Mô phỏng duyệt web thực tế
            html_content, login_url = self.simulate_real_browsing()
            
            # Bước 2: Trích xuất dữ liệu form
            form_data = self.extract_comprehensive_form_data(html_content)
            
            if not form_data:
                return {
                    'success': False,
                    'message': 'Không thể trích xuất các token đăng nhập cần thiết từ Facebook. Cấu trúc trang có thể đã thay đổi.',
                    'cookies': None
                }
            
            # Bước 3: Chuẩn bị payload đăng nhập thực tế
            login_payload = {
            'email': email,
            'pass': password,
            'login': 'Log In'  # Đây là giá trị của nút
            }
            
            # Thêm tất cả dữ liệu form đã trích xuất
            login_payload.update(form_data)
            
            print(f"🎯 Payload đăng nhập cuối cùng có {len(login_payload)} trường")
            print(f"📝 Các key trong payload: {list(login_payload.keys())}")
            
            # Bước 4: Thiết lập headers thực tế cho POST
            self.session.headers.update({
                'Referer': 'https://www.facebook.com/',
                'Origin': 'https://www.facebook.com',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1'
            })
            
            # Bước 5: Thêm độ trễ thực tế trước khi đăng nhập
            time.sleep(random.uniform(2, 5))
            
            # Bước 6: Thực hiện đăng nhập với endpoint phù hợp
            login_endpoint = 'https://www.facebook.com/login/device-based/regular/login/'
            
            # Thêm privacy mutation token vào URL nếu có
            if 'privacy_mutation_token' in form_data:
                login_endpoint += f'?privacy_mutation_token={form_data["privacy_mutation_token"]}&next'
            
            print(f"🔄 Đang gửi yêu cầu đăng nhập tới: {login_endpoint}")
            
            response = self.session.post(
                login_endpoint,
                data=login_payload,
                allow_redirects=True,
                timeout=30
            )
            
            print(f"📨 Phản hồi đăng nhập: {response.status_code}")
            print(f"📍 URL cuối cùng: {response.url}")
            
            # Bước 7: Kiểm tra kết quả
            return self.check_login_result(response, email, password, two_fa_code)
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Lỗi đăng nhập: {str(e)}',
                'cookies': None
            }
    
    def check_login_result(self, response, email, password, two_fa_code):
        """Kiểm tra kết quả đăng nhập nâng cao"""
        response_text = response.text.lower()
        response_url = response.url.lower()
        
        print(f"🔍 Đang phân tích phản hồi...")
        print(f"   Trạng thái: {response.status_code}")
        print(f"   URL: {response_url}")
        print(f"   Độ dài nội dung: {len(response.text)}")
        
        # Lưu phản hồi đầy đủ để debug
        with open('login_response_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Lưu thông tin phản hồi
        with open('login_debug_info.txt', 'w', encoding='utf-8') as f:
            f.write(f"URL phản hồi: {response.url}\n")
            f.write(f"Trạng thái phản hồi: {response.status_code}\n")
            f.write(f"Headers phản hồi: {dict(response.headers)}\n")
            f.write(f"Cookies phiên: {[f'{c.name}={c.value}' for c in self.session.cookies]}\n")
        
        print("💾 Các file debug đã được lưu: login_response_debug.html, login_debug_info.txt")
        
        # Kiểm tra cookies
        cookie_names = [cookie.name for cookie in self.session.cookies]
        print(f"🍪 Cookies nhận được: {cookie_names}")
        
        has_c_user = any(cookie.name == 'c_user' for cookie in self.session.cookies)
        has_xs = any(cookie.name == 'xs' for cookie in self.session.cookies)
        
        # Phát hiện thành công nâng cao
        success_indicators = {
            'cookies': has_c_user and has_xs,  # Có cookies quan trọng c_user và xs
            'url': any(pattern in response_url for pattern in [  # URL chuyển hướng đến trang chính
            'facebook.com/home', 'facebook.com/?sk=h_chr', 'facebook.com/?ref=',
            'facebook.com/feed', 'facebook.com/?_rdr'
            ]),
            'content': any(indicator in response_text for indicator in [  # Nội dung trang chính Facebook
            'feed_jewel', 'home_jewel', 'timeline', 'logout_form', 
            '"user_id"', 'composer', 'news_feed'
            ])
        }
        
        print(f"✅ Chỉ báo thành công: {success_indicators}")
        
        # Phát hiện lỗi nâng cao
        error_patterns = [  # Các mẫu lỗi đăng nhập
            'wrong password', 'incorrect password', 'login_error', 'error_box',
            'the password that you', 'your password was incorrect',
            'please re-enter your password', 'invalid username or password'
        ]
           
        has_errors = any(error in response_text for error in error_patterns)
        print(f"❌ Phát hiện lỗi: {has_errors}")
        
        # Kiểm tra thông báo lỗi cụ thể trong HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        error_divs = soup.find_all(['div', 'span'], class_=re.compile(r'error|Error'))
        for error_div in error_divs:
            if error_div.get_text(strip=True):
                print(f"🚨 Tìm thấy thông báo lỗi: {error_div.get_text(strip=True)[:100]}")
        
        # Phát hiện yêu cầu xác thực 2 yếu tố
        needs_2fa = any([
            'checkpoint' in response_url,  # URL checkpoint của Facebook
            'two-factor' in response_text,  # Nội dung về xác thực 2 yếu tố
            'approvals_code' in response_text,  # Mã xác thực
            'security check' in response_text  # Kiểm tra bảo mật
        ])
        
        print(f"🔐 Yêu cầu xác thực 2 yếu tố: {needs_2fa}")
        
        # Xử lý logic quyết định đăng nhập
        print("🔍 Bắt đầu xử lý logic quyết định đăng nhập...")
        
        # Kiểm tra xác thực 2 yếu tố
        if needs_2fa:
            print("🔐 Tài khoản yêu cầu xác thực 2 yếu tố")
            if two_fa_code:
                print(f"🔑 Đang xử lý mã 2FA: {two_fa_code}")
                return self.handle_2fa(two_fa_code, response)
            else:
                print("❌ Không có mã 2FA được cung cấp")
                return {
                    'success': False,
                    'message': 'Tài khoản yêu cầu xác thực 2 yếu tố. Vui lòng cung cấp mã 2FA.',
                    'cookies': None
                }       
        
        # Kiểm tra đăng nhập thành công
        if any(success_indicators.values()):
            print("✅ Phát hiện dấu hiệu đăng nhập thành công")
            # Kiểm tra cookies quan trọng
            if has_c_user == False and has_xs == False:
                print("❌ Không thể lấy được cookies quan trọng (c_user và xs)")
                return {
                'success': False,
                'message': 'Không thể đăng nhập để lấy cookies',
                'cookies': None
                }
                
            print("🍪 Đang lấy cookies từ phiên đăng nhập...")
            cookies = get_cookies_string(self.session)
            print("🎉 Đăng nhập thành công!")
            return {
            'success': True,
            'message': 'Đăng nhập thành công!',
            'cookies': cookies
            }
        
        # Kiểm tra lỗi đăng nhập
        if has_errors:
            print("❌ Phát hiện lỗi đăng nhập trong phản hồi")
            return {
            'success': False,
            'message': 'Email hoặc mật khẩu không hợp lệ. Vui lòng kiểm tra lại thông tin đăng nhập.',
            'cookies': None
            }
        
        # Kiểm tra nếu vẫn ở trang đăng nhập (báo hiệu thất bại)
        if 'login' in response_url or 'login' in response_text:
            print("⚠️ Vẫn ở trang đăng nhập - đăng nhập thất bại")
            return {
            'success': False,
            'message': 'Đăng nhập thất bại. Vui lòng kiểm tra file login_response_debug.html để biết chi tiết.',
            'cookies': None
            }
        
        # Trường hợp không xác định được trạng thái
        print("❓ Không thể xác định trạng thái đăng nhập")
        return {
            'success': False,
            'message': f'Trạng thái đăng nhập không rõ ràng. Kiểm tra các file debug. URL cuối cùng: {response.url}',
            'cookies': None
        }
    
    def handle_2fa(self, two_fa_code, login_response):
        """Xử lý xác thực 2 yếu tố với trích xuất form nâng cao"""
        try:
            print(f"🔐 Đang xử lý xác thực 2FA với mã: {two_fa_code}")
            
            # Lấy nội dung HTML từ phản hồi đăng nhập
            html_content = login_response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Trích xuất tất cả dữ liệu form từ trang 2FA
            form_data = {}
            print("🔍 Đang trích xuất dữ liệu form từ trang xác thực 2FA...")
            
            for form in soup.find_all('form'):
                for inp in form.find_all('input'):
                    name = inp.get('name')
                    if name:
                        value = inp.get('value', '')
                        form_data[name] = value
                        print(f"   📝 Tìm thấy trường: {name} = {value[:30]}...")
            
            print(f"✅ Đã trích xuất {len(form_data)} trường từ form 2FA")
            
            # Chuẩn bị payload cho việc gửi mã 2FA
            twofa_payload = {
                'approvals_code': two_fa_code,  # Mã xác thực 2FA
                'submit[Continue]': 'Continue',  # Nút tiếp tục
                'save_device': '1'  # Lưu thiết bị tin cậy
            }
            # Thêm tất cả dữ liệu form đã trích xuất
            twofa_payload.update(form_data)
            
            print(f"🎯 Payload 2FA cuối cùng có {len(twofa_payload)} trường")
            print(f"📝 Các trường chính: {list(twofa_payload.keys())}")
            
            # Gửi mã 2FA
            print("🔄 Đang gửi mã xác thực 2FA...")
            twofa_response = self.session.post(
                login_response.url,  # Sử dụng URL từ phản hồi đăng nhập
                data=twofa_payload,
                allow_redirects=True,
                timeout=20
            )
            
            print(f"📨 Phản hồi 2FA: {twofa_response.status_code}")
            print(f"📍 URL cuối cùng sau 2FA: {twofa_response.url}")
            
            # Kiểm tra kết quả sau khi xử lý 2FA
            return self.check_login_result(twofa_response, "", "", None)
            
        except Exception as e:
            print(f"❌ Lỗi xử lý 2FA: {str(e)}")
            return {
                'success': False,
                'message': f'Xử lý xác thực 2FA thất bại: {str(e)}',
                'cookies': None
            }
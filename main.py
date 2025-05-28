import tkinter as tk
from tkinter import messagebox, ttk
import threading
from datetime import datetime
from facebook_login import FacebookLogin
from utils import save_to_file, get_cookies_string

class FacebookLoginApp:
    def __init__(self):
        self.fb_login = FacebookLogin()
        self.setup_gui()
    
    def setup_gui(self):
        """Thiết lập giao diện người dùng chính"""
        self.root = tk.Tk()
        self.root.title("Đăng nhập Facebook Tự động")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Khung chính
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text="Đăng nhập Facebook Tự động", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Trường Email/Điện thoại
        ttk.Label(main_frame, text="Email/Điện thoại:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(main_frame, textvariable=self.email_var, width=40)
        email_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Trường Mật khẩu
        ttk.Label(main_frame, text="Mật khẩu:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=self.password_var, 
                                 show="*", width=40)
        password_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Trường 2FA
        ttk.Label(main_frame, text="Mã 2FA (tùy chọn):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.twofa_var = tk.StringVar()
        twofa_entry = ttk.Entry(main_frame, textvariable=self.twofa_var, width=40)
        twofa_entry.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Nút đăng nhập
        login_btn = ttk.Button(main_frame, text="Đăng nhập", 
                              command=self.start_login_thread)
        login_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Thanh tiến trình
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Nhãn trạng thái
        self.status_var = tk.StringVar(value="Sẵn sàng đăng nhập")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Vùng văn bản kết quả
        ttk.Label(main_frame, text="Kết quả:").grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.result_text = tk.Text(result_frame, height=8, width=60)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Thanh cuộn
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # Cấu hình trọng số lưới
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
    
    def start_login_thread(self):
        """Bắt đầu quá trình đăng nhập trong luồng riêng biệt"""
        # Kiểm tra đầu vào
        if not self.email_var.get().strip() or not self.password_var.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập email và mật khẩu!")
            return
        
        # Bắt đầu đăng nhập trong luồng riêng biệt
        login_thread = threading.Thread(target=self.perform_login)
        login_thread.daemon = True
        login_thread.start()
    
    def perform_login(self):
        """Thực hiện quá trình đăng nhập"""
        try:
            # Cập nhật giao diện người dùng
            self.root.after(0, self.update_status, "Đang đăng nhập...")
            self.root.after(0, self.progress.start)
            
            # Lấy thông tin đăng nhập
            email = self.email_var.get().strip()
            password = self.password_var.get().strip()
            two_fa = self.twofa_var.get().strip() if self.twofa_var.get().strip() else None
            
            # Thực hiện đăng nhập
            result = self.fb_login.login(email, password, two_fa)
            
            # Cập nhật giao diện người dùng với kết quả
            self.root.after(0, self.update_result, result, email, password, two_fa)
            
        except Exception as e:
            error_result = {
                'success': False,
                'message': f'Lỗi không mong đợi: {str(e)}',
                'cookies': None
            }
            self.root.after(0, self.update_result, error_result, "", "", "")
        finally:
            self.root.after(0, self.progress.stop)
    
    def update_status(self, message):
        """Cập nhật nhãn trạng thái"""
        self.status_var.set(message)
    
    def update_result(self, result, email, password, two_fa):
        """Cập nhật hiển thị kết quả"""
        self.result_text.delete(1.0, tk.END)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if result['success']:
            self.status_var.set("Đăng nhập thành công!")
            result_text = f"[{timestamp}] ✅ THÀNH CÔNG\n"
            result_text += f"Thông báo: {result['message']}\n"
            
            # Lưu vào file
            cookies = result.get('cookies', '')
            if cookies:
                data, file_name = save_to_file(email, password, two_fa or "", cookies)
                result_text += f"Thông tin tài khoản đã được lưu vào {file_name}\n"
            
            messagebox.showinfo("Thành công", "Đăng nhập thành công! Thông tin tài khoản đã được lưu.")
        else:
            self.status_var.set("Đăng nhập thất bại!")
            result_text = f"[{timestamp}] ❌ THẤT BẠI\n"
            result_text += f"Lỗi: {result['message']}\n"
            
            messagebox.showerror("Thất bại", result['message'])
        
        self.result_text.insert(tk.END, result_text)
    
    def run(self):
        """Chạy ứng dụng"""
        self.root.mainloop()

if __name__ == "__main__":
    app = FacebookLoginApp()
    app.run()
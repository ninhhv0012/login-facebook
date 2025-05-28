# Tự động đăng nhập facebook

## Cấu trúc file

```

├── main.py              # GUI
├── facebook_login.py    # Xử lý logic đăng nhập
├── utils.py            # Các hàm Utility 
├── setup.py            # Cài đặt thư viện và chạy chương trình
├── requirements.txt    # Thư viện python
└── README.md          # File hướng dẫn
```

## Cài đặt


## Cách sử dụng

1. **Chạy chương trình:**

   - Cách 1:
   Python version 3.10

   ```bash
   python -m venv venv
   venv\Scripts\activate
   python setup.py
   ```
   - Cách 2:
   Mở file app.exe

2. **Nhập thông tin:**
   - Email hoặc số điện thoại
   - Password
   - 2FA code (nếu có)

3. **Nhấn "Login"**


4. **Kết quả:**
   - Thành công: Thông tin tài khoản sẽ được lưu vào thư mục cookies `account_xxxx.txt`
   - Thất bại: Hiển thị thông tin lỗi và xem chi tiết lỗi tại 2 file: login_debug_info.txt và login_response_debug.html



## Cách hoạt động

### Quá trình đăng nhập
1. Tải Trang: Lấy trang đăng nhập của Facebook
2. Trích Xuất Token: Trích xuất các token ẩn trong biểu mẫu (lsd, jazoest, fb_dtsg)
3. Yêu Cầu Đăng Nhập: Gửi yêu cầu POST kèm theo thông tin đăng nhập
4. Phân Tích Phản Hồi: Kiểm tra các chỉ báo thành công
5. Xử Lý Xác Thực Hai Yếu Tố (2FA): Xử lý khi hệ thống yêu cầu xác thực hai bước
6. Lưu Cookie: Lưu cookie phiên làm việc

### Phát Hiện Đăng Nhập Thành Công
- Sự xuất hiện của cookie c_user
- URL được chuyển hướng về trang chủ hoặc bảng tin
- Phân tích nội dung HTML để kiểm tra trạng thái đã đăng nhập

## Chi Tiết Kỹ Thuật

- Chuỗi User-Agent giống trình duyệt thật
- Header Accept phù hợp




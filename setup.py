# setup.py - Script cài đặt và thiết lập
import subprocess
import sys
import os

def install_requirements():
    """Cài đặt các gói cần thiết"""
    try:
        print("Đang cài đặt các gói cần thiết...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "requests", "beautifulsoup4", "lxml"
        ])
        print("✅ Đã cài đặt thành công tất cả các gói!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi cài đặt các gói: {e}")
        return False
    return True

def main():
    """Hàm thiết lập chính"""
    print("🚀 Đăng nhập Facebook tự động - Thiết lập")
    print("=" * 40)
    
    # Cài đặt các gói yêu cầu
    if not install_requirements():
        return
    

    
    print("\n✅ Thiết lập hoàn tất thành công!")
    print("\nĐể chạy ứng dụng:")
    print("python main.py")

    try:
        import main
        app = main.FacebookLoginApp()
        app.run()
    except Exception as e:
        print(f"❌ Lỗi khi chạy ứng dụng: {e}")

if __name__ == "__main__":
    main()
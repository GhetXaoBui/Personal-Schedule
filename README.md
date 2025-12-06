Personal Schedule Assistant
Một công cụ lập lịch cá nhân với xử lý ngôn ngữ tiếng Việt và cơ sở dữ liệu SQLite.
Tính năng chính
1. Quản lý sự kiện
Thêm sự kiện bằng tiếng Việt tự nhiên
Sửa/Xóa sự kiện dễ dàng
Xem theo nhiều chế độ: Ngày, Tuần, Tháng
Tìm kiếm sự kiện theo từ khóa
Nhập/Xuất dữ liệu JSON
2. Giao diện dễ sử dụng
List sự kiện, thời gian, địa điểm
Điều hướng linh hoạt giữa ngày/tháng/năm
Sử dụng tiếng Việt

Yêu cầu hệ thống
python 3.10 trở lên
khuyến nghị sử dụng python 3.11.9
hệ điều hành windows

Hướng dẫn cài đặt
pip install -r requirements.txt


cấu trúc thư mục
PSA/
├── main.py              # Điểm khởi chạy chính
├── main_window.py       # Giao diện chính
├── database.py          # Thao tác cơ sở dữ liệu
├── models.py            # Định nghĩa dữ liệu
├── nlp_processor.py     # Xử lý ngôn ngữ tự nhiên
├── file_handler.py      # Xử lý file JSON
├── test_nlp.py          # Kiểm tra NLP
├── requirements.txt     # Thư viện cần thiết
└── README.md            # Tài liệu

Chạy chương trình
python main.py

Kiểm tra độ chính xác
python test_nlp.py


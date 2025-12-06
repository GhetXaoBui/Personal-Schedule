import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from nlp_processor import UndertheseaNLPProcessor
import re


class NLPTester:
    def __init__(self):
        self.processor = UndertheseaNLPProcessor()
        self.test_cases = []
        self.results = []
        self.prepare_test_cases()
    
    def prepare_test_cases(self):
        now = datetime.now()
        today = now.date()
        
        # Định dạng: (input_text, expected_output_dict)
        self.test_cases = [
            {
                "input": "họp nhóm ở phòng 302 lúc 10h",
                "expected": {
                    "event": "họp nhóm",
                    "hour": 10,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "họp nhóm lúc 10 giờ ở phòng 302",
                "expected": {
                    "event": "họp nhóm",
                    "hour": 10,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "gặp khách hàng lúc 10:30 tại quán cà phê",
                "expected": {
                    "event": "gặp khách hàng",
                    "hour": 10,
                    "minute": 30,
                    "has_location": True
                }
            },
            {
                "input": "thảo luận dự án lúc 14h30 ở công ty",
                "expected": {
                    "event": "thảo luận dự án",
                    "hour": 14,
                    "minute": 30,
                    "has_location": True
                }
            },
            {
                "input": "ăn tối lúc 19:00 tại nhà hàng ABC",
                "expected": {
                    "event": "ăn tối",
                    "hour": 19,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "học bài lúc 8h sáng tại thư viện",
                "expected": {
                    "event": "học bài",
                    "hour": 8,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "họp chiều lúc 14h tại phòng 101",
                "expected": {
                    "event": "họp chiều",
                    "hour": 14,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "sinh nhật lúc 7h tối tại nhà",
                "expected": {
                    "event": "sinh nhật",
                    "hour": 19,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "tập thể dục lúc 6h sáng tại công viên",
                "expected": {
                    "event": "tập thể dục",
                    "hour": 6,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "xem phim lúc 9h tối ở rạp CGV",
                "expected": {
                    "event": "xem phim",
                    "hour": 21,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "họp nhóm sáng mai lúc 9h",
                "expected": {
                    "event": "họp nhóm",
                    "hour": 9,
                    "minute": 0,
                    "has_location": False
                }
            },
            {
                "input": "đi chơi ngày mai lúc 15h tại công viên",
                "expected": {
                    "event": "đi chơi",
                    "hour": 15,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "làm việc hôm nay lúc 13h ở công ty",
                "expected": {
                    "event": "làm việc",
                    "hour": 13,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "khám bệnh mai lúc 8h30 tại bệnh viện",
                "expected": {
                    "event": "khám bệnh",
                    "hour": 8,
                    "minute": 30,
                    "has_location": True
                }
            },
            {
                "input": "nộp bài hôm nay lúc 17h",
                "expected": {
                    "event": "nộp bài",
                    "hour": 17,
                    "minute": 0,
                    "has_location": False
                }
            },
            {
                "input": "họp công ty thứ hai lúc 10h",
                "expected": {
                    "event": "họp công ty",
                    "hour": 10,
                    "minute": 0,
                    "has_location": False
                }
            },
            {
                "input": "học thêm thứ 3 lúc 18h tại trung tâm",
                "expected": {
                    "event": "học thêm",
                    "hour": 18,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "chơi bóng thứ tư lúc 17h30 ở sân vận động",
                "expected": {
                    "event": "chơi bóng",
                    "hour": 17,
                    "minute": 30,
                    "has_location": True
                }
            },
            {
                "input": "đi ăn thứ 5 lúc 19h tại nhà hàng",
                "expected": {
                    "event": "đi ăn",
                    "hour": 19,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "xem phim thứ sáu lúc 20h ở rạp",
                "expected": {
                    "event": "xem phim",
                    "hour": 20,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "du lich cuoi tuan luc 8h sang",
                "expected": {
                    "event": "du lich",
                    "hour": 8,
                    "minute": 0,
                    "has_location": False
                }
            },
            {
                "input": "di choi chu nhat luc 14h tai cong vien",
                "expected": {
                    "event": "di choi",
                    "hour": 14,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "gap ban than thu 7 luc 10h o quan ca phe",
                "expected": {
                    "event": "gap ban than",
                    "hour": 10,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "lam viec nhom tuần sau luc 9h",
                "expected": {
                    "event": "lam viec nhom",
                    "hour": 9,
                    "minute": 0,
                    "has_location": False
                }
            },
            {
                "input": "hop bao cuoi tuan luc 15h",
                "expected": {
                    "event": "hop bao",
                    "hour": 15,
                    "minute": 0,
                    "has_location": False
                }
            },
            {
                "input": "tiệc tùng lúc 20h tối nay tại club",
                "expected": {
                    "event": "tiệc tùng",
                    "hour": 20,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "ôn thi lúc 7h tối mai tại nhà",
                "expected": {
                    "event": "ôn thi",
                    "hour": 19,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "thuyết trình lúc 13h30 tại phòng hội thảo",
                "expected": {
                    "event": "thuyết trình",
                    "hour": 13,
                    "minute": 30,
                    "has_location": True
                }
            },
            {
                "input": "mua sắm lúc 10h sáng thứ bảy tại siêu thị",
                "expected": {
                    "event": "mua sắm",
                    "hour": 10,
                    "minute": 0,
                    "has_location": True
                }
            },
            {
                "input": "đón khách lúc 8h sáng mai ở sân bay",
                "expected": {
                    "event": "đón khách",
                    "hour": 8,
                    "minute": 0,
                    "has_location": True
                }
            }
        ]
    
    def normalize_text(self, text):
        if not text:
            return ""
        # Chuyển về chữ thường, bỏ dấu đơn giản
        text = text.lower().strip()
        text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text)
        text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
        text = re.sub(r'[ìíịỉĩ]', 'i', text)
        text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
        text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
        text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
        text = re.sub(r'[đ]', 'd', text)
        return ' '.join(text.split())
    
    def contains_keywords(self, actual_text, expected_text):
        if not actual_text or not expected_text:
            return False
        
        # Lấy các từ quan trọng (bỏ stop words)
        stop_words = {'va', 'voi', 'cho', 'tu', 'den', 'o', 'tai', 'trong', 
                     'ngoai', 'tren', 'duoi', 'truoc', 'sau', 'giua', 'bang', 
                     'theo', 've', 'luc', 'sang', 'chieu', 'toi', 'trua', 
                     'dem', 'gio', 'h', 'ngay', 'hom', 'mai', 'nay', 'qua'}
        
        expected_words = set(expected_text.split())
        expected_keywords = [w for w in expected_words if w not in stop_words and len(w) > 1]
        
        if not expected_keywords:
            expected_keywords = list(expected_words)
        
        matched = 0
        for keyword in expected_keywords:
            if keyword in actual_text:
                matched += 1
        
        return matched >= max(1, len(expected_keywords) * 0.5)
    
    def compare_results(self, actual_event, expected):
        """So sánh kết quả thực tế với mong đợi."""
        try:
            # 1. Kiểm tra tên sự kiện
            actual_name = self.normalize_text(actual_event.event_name)
            expected_name = self.normalize_text(expected["event"])
            
            if not self.contains_keywords(actual_name, expected_name):
                return False, "Tên sự kiện sai"
            
            # 2. Kiểm tra giờ
            actual_hour = actual_event.start_time.hour
            expected_hour = expected["hour"]
            
            hour_diff = abs(actual_hour - expected_hour)
            if hour_diff > 2 and hour_diff not in [12, 11, 13]:  # Cho phép AM/PM nhầm
                return False, f"Giờ sai: {actual_hour} giờ (mong đợi: {expected_hour} giờ)"
            
            # 3. Kiểm tra phút
            actual_minute = actual_event.start_time.minute
            expected_minute = expected["minute"]
            
            if abs(actual_minute - expected_minute) > 5:
                return False, f"Phút sai: {actual_minute} phút (mong đợi: {expected_minute} phút)"
            
            # 4. Kiểm tra địa điểm
            actual_has_location = actual_event.location is not None and actual_event.location.strip() != ""
            expected_has_location = expected["has_location"]
            
            if actual_has_location != expected_has_location:
                loc_status = "có" if actual_has_location else "không có"
                loc_expected = "có" if expected_has_location else "không có"
                return False, f"Địa điểm: {loc_status} (mong đợi: {loc_expected})"
            
            return True, ""
        except Exception as e:
            return False, f"Lỗi so sánh: {e}"
    
    def run_tests(self):
        print("=" * 80)
        print("KIỂM TRA NLP PROCESSOR")
        print("=" * 80)
        
        total_tests = len(self.test_cases)
        passed_tests = 0
        failed_tests = []
        
        for i, test in enumerate(self.test_cases, 1):
            try:
                # Parse với NLP processor
                event = self.processor.parse_text(test['input'])
                
                if event:
                    # So sánh kết quả
                    is_correct, reason = self.compare_results(event, test['expected'])
                    
                    if is_correct:
                        passed_tests += 1
                    else:
                        # Thêm vào danh sách câu sai
                        failed_tests.append({
                            "test_id": i,
                            "input": test['input'],
                            "actual_event": event,
                            "expected": test['expected'],
                            "reason": reason
                        })
                else:
                    # Không tạo được event
                    failed_tests.append({
                        "test_id": i,
                        "input": test['input'],
                        "actual_event": None,
                        "expected": test['expected'],
                        "reason": "Không tạo được event"
                    })
                    
            except Exception as e:
                failed_tests.append({
                    "test_id": i,
                    "input": test['input'],
                    "actual_event": None,
                    "expected": test['expected'],
                    "reason": f"Lỗi xử lý: {e}"
                })
        
        # Hiển thị các câu sai
        if failed_tests:
            print(f"\nCÁC CÂU SAI ({len(failed_tests)}/{total_tests}):")
            print("-" * 80)
            
            for fail in failed_tests:
                print(f"\nTest {fail['test_id']}: {fail['input']}")
                print(f"  Lý do: {fail['reason']}")
                
                if fail['actual_event']:
                    event = fail['actual_event']
                    location = event.location if event.location else "Không có"
                    print(f"  Kết quả thực tế: {event.event_name} lúc {event.start_time.strftime('%H:%M')} tại {location}")
                
                expected = fail['expected']
                location_expected = "có địa điểm" if expected['has_location'] else "không có địa điểm"
                print(f"  Kết quả mong đợi: {expected['event']} lúc {expected['hour']:02d}:{expected['minute']:02d} ({location_expected})")
        else:
            print(f"\nKHÔNG CÓ CÂU NÀO SAI! (100% chính xác)")
        
        # Tính tỉ lệ chính xác
        accuracy = (passed_tests / total_tests) * 100
        print("\n" + "=" * 80)
        print("TỔNG KẾT")
        print("=" * 80)
        print(f"Tổng test cases: {total_tests}")
        print(f"Số câu đúng: {passed_tests}")
        print(f"Số câu sai: {len(failed_tests)}")
        print(f"Độ chính xác: {accuracy:.1f}%")
        print("-" * 80)
        
        if accuracy >= 80:
            print(" ĐẠT YÊU CẦU (≥80%)")
        else:
            print(" KHÔNG ĐẠT YÊU CẦU (<80%)")
        
        return accuracy, failed_tests


def main():
    tester = NLPTester()
    print("=" * 80)
    
    accuracy, failed_tests = tester.run_tests()
    
    # Hiển thị phân tích lỗi
    if failed_tests:
        print("\nPHÂN TÍCH LỖI:")
        print("-" * 80)
        
        error_counts = {
            "Tên sự kiện sai": 0,
            "Giờ sai": 0,
            "Phút sai": 0,
            "Địa điểm sai": 0,
            "Không tạo event": 0,
            "Lỗi xử lý": 0
        }
        
        for fail in failed_tests:
            reason = fail['reason']
            if "Tên sự kiện sai" in reason:
                error_counts["Tên sự kiện sai"] += 1
            elif "Giờ sai" in reason:
                error_counts["Giờ sai"] += 1
            elif "Phút sai" in reason:
                error_counts["Phút sai"] += 1
            elif "Địa điểm" in reason:
                error_counts["Địa điểm sai"] += 1
            elif "Không tạo được event" in reason:
                error_counts["Không tạo event"] += 1
            elif "Lỗi xử lý" in reason:
                error_counts["Lỗi xử lý"] += 1
        
        for error_type, count in error_counts.items():
            if count > 0:
                print(f"- {error_type}: {count} câu")
    
    print("\n" + "=" * 80)
    return accuracy


if __name__ == "__main__":
    try:
        accuracy = main()
        sys.exit(0 if accuracy >= 80 else 1)
    except KeyboardInterrupt:
        print("\n\nĐã dừng kiểm tra!")
        sys.exit(1)
    except Exception as e:
        print(f"\nLỗi không mong muốn: {e}")
        sys.exit(1)
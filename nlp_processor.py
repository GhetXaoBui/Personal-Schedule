import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from models import Event
from underthesea import word_tokenize, pos_tag, ner


class UndertheseaNLPProcessor:
    def __init__(self):
        self.now = datetime.now()
        
        # Khởi tạo patterns và keywords
        self._initialize_patterns()
        self._initialize_keywords()
        
        # Các từ lọc bỏ (dừng) phổ biến của tiếng Việt
        self.stop_words = {
            'và', 'với', 'cho', 'từ', 'đến', 'ở', 'tại', 'trong', 'ngoài',
            'trên', 'dưới', 'trước', 'sau', 'giữa', 'bằng', 'theo', 'về',
            
            'va', 'voi', 'cho', 'tu', 'den', 'o', 'tai', 'trong', 'ngoai',
            'tren', 'duoi', 'truoc', 'sau', 'giua', 'bang', 'theo', 've'
        }
        
        # Động từ liên quan đến sự kiện
        self.event_verbs = {
            'họp', 'gặp', 'gặp gỡ', 'thảo luận', 'bàn', 'trao đổi',
            'sinh nhật', 'tiệc', 'liên hoan', 'kỷ niệm',
            'học', 'ôn tập', 'làm bài', 'nghiên cứu',
            'làm việc', 'làm', 'công việc', 'dự án',
            'đi', 'đi chơi', 'du lịch', 'thăm',
            'ăn', 'uống', 'cà phê', 'trà',
            'chơi', 'giải trí', 'thể thao', 'tập',
            
            'hop', 'gap', 'gap go', 'thao luan', 'ban', 'trao doi',
            'sinh nhat', 'tiec', 'lien hoan', 'ky niem',
            'hoc', 'on tap', 'lam bai', 'nghien cuu',
            'lam viec', 'lam', 'cong viec', 'du an',
            'di', 'di choi', 'du lich', 'tham',
            'an', 'uong', 'ca phe', 'tra',
            'choi', 'giai tri', 'the thao', 'tap',
        }
        
        print("Underthesea NLP Processor initialized")
    
    def _initialize_patterns(self):
        """Initialize regex patterns for backup parsing."""
        # Time_patterns - thêm cả không dấu
        self.time_patterns = [
            r'(?:lúc|luc|vào lúc|vao luc|vào khoảng|vao khoang|khoảng|khoang)\s*(\d{1,2})\s*(?:giờ|gio|h|:)\s*(\d{0,2})?\s*(sáng|sang|chiều|chieu|tối|toi|trưa|trua|đêm|dem|am|pm)?',
            r'(\d{1,2})\s*(?:giờ|gio|h|:)\s*(\d{0,2})?\s*(sáng|sang|chiều|chieu|tối|toi|trưa|trua|đêm|dem|am|pm)',
            r'(\d{1,2})\s*(?:giờ|gio|h|:)\s*(\d{0,2})?',
            r'(sáng|sang|chiều|chieu|tối|toi|trưa|trua|đêm|dem)\s*(\d{1,2})\s*(?:giờ|gio|h)',
        ]
    
    # location_patterns - thêm cả không dấu
        self.location_patterns = [
            r'(?:ở|o|tại|tai|tại địa điểm|tai dia diem|ở phòng|o phong|tại phòng|tai phong|tại tầng|tai tang|ở tầng|o tang|tại công ty|tai cong ty|ở công ty|o cong ty|tại nhà|tai nha|ở nhà|o nha|tại quán|tai quan|ở quán|o quan|tại trường|tai truong|ở trường|o truong)\s+([^,.;]{2,50}?)(?=\s+(?:lúc|luc|\d{1,2}(?:\s*(?:giờ|gio|h|:))|sáng|sang|chiều|chieu|tối|toi|trưa|trua|đêm|dem|$|và|va|rồi|roi))',
            r'(?:ở|o|tại|tai)\s+([^,.;]{2,50})(?=\s|$)',
        ]
    def _initialize_keywords(self):
        """Initialize date and time keywords."""
        self.date_keywords = {
            'mai': 1, 'ngày mai': 1,
            'hôm nay': 0, 'hôm qua': -1,
            'tuần sau': 7, 'tuần tới': 7, 'tuần trước': -7,
            'tháng sau': 30, 'tháng tới': 30, 'tháng trước': -30,
            'năm sau': 365, 'năm tới': 365, 'năm trước': -365,
        }
        
        # Days of week
        self.days_of_week = {
            'thứ hai': 0, 'thứ 2': 0,
            'thứ ba': 1, 'thứ 3': 1,
            'thứ tư': 2, 'thứ 4': 2,
            'thứ năm': 3, 'thứ 5': 3,
            'thứ sáu': 4, 'thứ 6': 4,
            'thứ bảy': 5, 'thứ 7': 5,
            'chủ nhật': 6, 'cn': 6,
        }
    
    def parse_text(self, text: str) -> Optional[Event]:
        if not text or len(text.strip()) < 3:
            return None
        
        print(f"\nParsing Input: '{text}'")
        
        try:
            # Step 1: Phân tích NLP bằng thư viện Underthesea
            tokens = word_tokenize(text)
            pos_tags = pos_tag(text)
            ner_result = ner(text)
            
            print(f"Tokens: {tokens}")
            print(f"POS Tags: {pos_tags}")
            print(f"NER: {ner_result}")
            
            # Step 2: Trích xuất thành phần bằng phân tích Underthesea
            components = self._extract_with_underthesea(text, tokens, pos_tags, ner_result)
            
            # Step 3: Khi phân tích Underthesea thất bại, dùng phương pháp rule-based thay thế
            if not components or 'event_name' not in components:
                print("Underthesea extraction failed, using rule-based fallback")
                return self._parse_with_rules(text.lower())
            
            # Step 4: Tạo datetime
            start_time = self._create_datetime(
                components.get('hour', 9),
                components.get('minute', 0),
                components.get('date_offset', 0)
            )
            
            # Step 5: Tạo sự kiện và trả kết quả
            event = Event(
                event_name=components['event_name'],
                start_time=start_time,
                end_time=start_time + timedelta(hours=1),
                location=components.get('location'),
                reminder_minutes=15
            )
            
            print(f"Success Created: {event.event_name} at {event.start_time}")
            return event
            
        except Exception as e:
            print(f"Error Underthesea parsing failed: {e}")
            # Chuyển sang phân tích dựa trên rule-based
            return self._parse_with_rules(text.lower())
    
    def _extract_with_underthesea(self, text: str, tokens, pos_tags, ner_result):
        # Trích xuất các thành phần sự kiện bằng Underthesea.
        components = {}
        
        # 1. Phân tích tên sự kiện thông qua POS tags
        event_name = self._extract_event_name_from_pos(pos_tags, text)
        if event_name:
            components['event_name'] = event_name
        
        # 2. Phân tích địa điểm thông qua NER
        location = self._extract_location_from_ner(ner_result)
        if not location:
            # Thử rule-based phân tích nếu NER không dùng được
            location = self._extract_location(text.lower())
        components['location'] = location
        
        # 3. Lấy thời gian
        time_info = self._extract_time_info(text.lower())
        if time_info:
            components.update(time_info)
        else:
            # Default time
            components['hour'] = 9
            components['minute'] = 0
        
        # 4. Phân tích khoảng cách ngày
        components['date_offset'] = self._extract_date_offset(text.lower())
        
        print(f"[Components] {components}")
        return components
    
    def _extract_event_name_from_pos(self, pos_tags, original_text):
        # Trích xuất tên sự kiện bằng cách sử dụng POS
        event_words = []
        
        # Strategy 1: Xác định cụm động từ
        for word, pos in pos_tags:
            if pos.startswith('V') or pos.startswith('N'):  # Verbs or nouns
                # Bỏ các từ nối và giới từ thông dụng
                if word.lower() in ['lúc', 'ở', 'tại', 'vào', 'từ', 'đến', 'luc', 'o', 'tai', 'vao', 'tu', 'den']:
                    break
                event_words.append(word)
            elif pos == 'CH':  # Dấu câu - thường đánh dấu kết thúc mô tả event
                break
        
        # Strategy 2: Nếu không tìm thấy động từ phù hợp, lấy một vài từ có nghĩa đầu tiên
        if not event_words or len(' '.join(event_words)) < 2:
            for word, pos in pos_tags[:3]:  # First 3 tokens
                if pos != 'CH' and word.lower() not in ['lúc', 'ở', 'tại', 'luc']:
                    event_words.append(word)
        
        event_name = ' '.join(event_words).strip()
        
        # Clean up
        if event_name:
            # Capitalize first letter
            event_name = event_name[0].upper() + event_name[1:] if event_name else "Sự kiện"
            
            # Remove trailing prepositions
            event_name = re.sub(r'\s+(lúc|ở|tại|vào)$', '', event_name, flags=re.IGNORECASE)
        
        return event_name if event_name and len(event_name) > 1 else None
    
    def _extract_location_from_ner(self, ner_result):
        # Trích xuất vị trí từ NER
        locations = []
        
        for entity in ner_result:
            if entity[3] in ['LOC', 'ORG', 'FAC']:  # Location, Organization, Facility
                locations.append(entity[0])
        
        if locations:
            return ' '.join(locations)
        
        return None
    
    def _extract_time_info(self, text: str) -> Optional[Dict[str, int]]:
        # Trích xuất thời gian từ câu đầu vào
        for pattern in self.time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._parse_time_match(match)
        
        return None
    
    def _parse_time_match(self, match: re.Match) -> Dict[str, int]:
        """Parse time from regex match."""
        try:
            groups = match.groups()
            hour, minute, period = None, 0, None
            
            # Pattern matching logic
            if len(groups) >= 3 and groups[0] and groups[2]:
                hour = int(groups[0])
                minute = int(groups[1]) if groups[1] and groups[1].isdigit() else 0
                period = groups[2]
            elif len(groups) >= 2 and groups[0]:
                hour = int(groups[0])
                if groups[1] and groups[1].isdigit():
                    minute = int(groups[1])
                elif groups[1]:
                    period = groups[1]
            elif len(groups) >= 1 and groups[0]:
                hour = int(groups[0])
            
            if hour is None:
                return {'hour': 9, 'minute': 0}
            
            # Điều chỉnh cho định dạng 12 giờ
            if period:
                period_lower = period.lower()
                if period_lower in ['chiều', 'tối', 'đêm', 'pm', 'chieu', 'toi', 'dem']:
                    if hour < 12:
                        hour += 12
                elif period_lower in ['sáng', 'am', 'sang']:
                    if hour == 12:
                        hour = 0
            
            hour = hour % 24
            return {'hour': hour, 'minute': minute}
            
        except Exception:
            return {'hour': 9, 'minute': 0}
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text."""
        for pattern in self.location_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 1:
                    location_text = match.group(1).strip()
                    if location_text:
                        cleaned = self._clean_location_text(location_text)
                        if cleaned and len(cleaned) > 1:
                            return cleaned
        
        return None
    
    def _clean_location_text(self, text: str) -> str:
        """Clean and format location text."""
        time_words = ['lúc', 'sáng', 'chiều', 'tối', 'trưa', 'đêm', 'giờ', 'h', 'luc', 'sang', 'trua', 'chieu', 'toi', 'dem', 'gio']
        for word in time_words:
            text = re.sub(r'\b' + re.escape(word) + r'\b', '', text, flags=re.IGNORECASE)
        
        text = ' '.join(text.split())
        text = text.strip(' ,.-')
        
        if text:
            return ' '.join(word.capitalize() for word in text.split())
        
        return text
    
    def _extract_date_offset(self, text: str) -> int:
        """Extract date offset from text."""
        for keyword, offset in self.date_keywords.items():
            if keyword in text:
                return offset
        
        for day_name, day_num in self.days_of_week.items():
            if day_name in text:
                current_weekday = self.now.weekday()
                days_ahead = day_num - current_weekday
                if days_ahead <= 0:
                    days_ahead += 7
                return days_ahead
        
        return 0
    
    def _parse_with_rules(self, text: str) -> Optional[Event]:
        """Fallback rule-based parsing."""    
        date_offset = self._extract_date_offset(text)
        time_info = self._extract_time_info(text) or {'hour': 9, 'minute': 0}
        location = self._extract_location(text)
        
        # Simple event name extraction for fallback
        event_name = text
        for pattern in self.time_patterns + self.location_patterns:
            event_name = re.sub(pattern, '', event_name, flags=re.IGNORECASE)
        event_name = ' '.join(event_name.split()[:3]).strip()
        if not event_name:
            event_name = "Sự kiện"
        
        start_time = self._create_datetime(
            time_info['hour'],
            time_info['minute'],
            date_offset
        )
        
        return Event(
            event_name=event_name,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            location=location,
            reminder_minutes=15
        )
    
    def _create_datetime(self, hour: int, minute: int, date_offset: int) -> datetime:
        """Create datetime from components."""
        base_date = self.now.date() + timedelta(days=date_offset)
        
        try:
            return datetime.combine(base_date, datetime.min.time()).replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
        except ValueError:
            return self.now.replace(hour=hour % 24, minute=minute, second=0, microsecond=0)
    
    def _validate_event(self, event: Event) -> bool:
        """Validate parsed event."""
        return bool(event.event_name and event.start_time)
    
    def debug_parse(self, text: str):
        """Debug method to see parsing steps."""
        print(f"\n{'='*60}")
        print(f"Debug Parsing: '{text}'")
        print('-'*60)
        
        event = self.parse_text(text)
        if event:
            print(f"\n Created Event:")
            print(f"  Name: {event.event_name}")
            print(f"  Time: {event.start_time.strftime('%H:%M %d/%m/%Y')}")
            print(f"  Location: {event.location or 'Không có'}")
        else:
            print("\n Failed to create event")
        
        return event
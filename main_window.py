import sys
from datetime import datetime, date, timedelta
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QFileDialog,
    QLineEdit, QGroupBox, QHeaderView, QRadioButton, QButtonGroup,
    QCheckBox, QTextEdit, QScrollArea, QFrame, QSizePolicy, QInputDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QAction

from models import Event
from database import Database
from file_handler import FileHandler
from nlp_processor import UndertheseaNLPProcessor


class MainWindow(QMainWindow):
    """Main application window with simple interface."""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.file_handler = FileHandler()
        self.nlp_processor = UndertheseaNLPProcessor()
        self.current_view = "week"
        self.current_date = date.today()
        self.current_events = []  # Lưu trữ các sự kiện hiện tại để tìm kiếm
        
        self.setup_ui()
        self.load_events()
    
    def setup_ui(self):
        """Setup the main window UI as shown in image."""
        self.setWindowTitle("Personal Schedule Assistant")
        self.setGeometry(100, 100, 900, 700) 
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Personal Schedule Assistant")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # NLP Input Section
        nlp_group = QGroupBox("Nhập sự kiện bằng tiếng Việt tự nhiên")
        nlp_layout = QVBoxLayout()
        
        self.nlp_input = QLineEdit()
        self.nlp_input.setPlaceholderText('Ví dụ: "Họp nhóm lúc 10h sáng mai ở phòng 302"')
        self.nlp_input.returnPressed.connect(self.add_event_nlp)
        nlp_layout.addWidget(self.nlp_input)
        
        nlp_button_layout = QHBoxLayout()
        add_button = QPushButton("Thêm sự kiện")
        add_button.clicked.connect(self.add_event_nlp)
        nlp_button_layout.addWidget(add_button)
        
        clear_button = QPushButton("Xóa")
        clear_button.clicked.connect(lambda: self.nlp_input.clear())
        nlp_button_layout.addWidget(clear_button)
        
        nlp_layout.addLayout(nlp_button_layout)
        nlp_group.setLayout(nlp_layout)
        main_layout.addWidget(nlp_group)
        
        # Search Section
        search_group = QGroupBox("Tìm kiếm sự kiện")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập từ khóa tìm kiếm...")
        self.search_input.returnPressed.connect(self.search_events)
        search_layout.addWidget(self.search_input)
        
        search_button = QPushButton("🔍 Tìm kiếm")
        search_button.clicked.connect(self.search_events)
        search_button.setMinimumWidth(100)
        search_layout.addWidget(search_button)
        
        clear_search_button = QPushButton("Xóa tìm kiếm")
        clear_search_button.clicked.connect(self.clear_search)
        clear_search_button.setMinimumWidth(100)
        search_layout.addWidget(clear_search_button)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # View Mode Selection
        view_group = QGroupBox("Chế độ xem")
        view_layout = QHBoxLayout()
        
        self.day_radio = QRadioButton("Ngày")
        self.week_radio = QRadioButton("Tuần")
        self.month_radio = QRadioButton("Tháng")
        
        self.week_radio.setChecked(True)  # Default to week view
        
        view_button_group = QButtonGroup(self)
        view_button_group.addButton(self.day_radio)
        view_button_group.addButton(self.week_radio)
        view_button_group.addButton(self.month_radio)
        
        view_button_group.buttonClicked.connect(self.change_view)
        
        view_layout.addWidget(self.day_radio)
        view_layout.addWidget(self.week_radio)
        view_layout.addWidget(self.month_radio)
        
        # Date navigation
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("◀")
        self.prev_button.clicked.connect(self.prev_period)
        nav_layout.addWidget(self.prev_button)
        
        self.date_label = QLabel(self.get_date_range_text())
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.date_label)
        
        self.next_button = QPushButton("▶")
        self.next_button.clicked.connect(self.next_period)
        nav_layout.addWidget(self.next_button)
        
        self.today_button = QPushButton("Hôm nay")
        self.today_button.clicked.connect(self.go_to_today)
        nav_layout.addWidget(self.today_button)
        
        view_layout.addStretch()
        view_layout.addLayout(nav_layout)
        
        view_group.setLayout(view_layout)
        main_layout.addWidget(view_group)
        
        # Bảng sự kiện
        table_group = QGroupBox("Danh sách sự kiện")
        table_layout = QVBoxLayout()
        
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(4)
        self.events_table.setHorizontalHeaderLabels(["Ngày", "Thời gian", "Địa điểm", "Sự kiện"])
        self.events_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.events_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.events_table.setAlternatingRowColors(True)
        
        # Set column widths
        self.events_table.setColumnWidth(0, 100)  # Ngày
        self.events_table.setColumnWidth(1, 80)   # Thời gian
        self.events_table.setColumnWidth(2, 150)  # Địa điểm
        self.events_table.horizontalHeader().setStretchLastSection(True)  # Sự kiện
        
        table_layout.addWidget(self.events_table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group, 1)  # Stretch factor 1
        
        # Event Details & Actions
        bottom_layout = QHBoxLayout()
        
        # Chi tiết sự kiện
        details_group = QGroupBox("Chi tiết sự kiện")
        details_layout = QVBoxLayout()
        
        self.event_name_label = QLabel("Chọn một sự kiện để xem chi tiết")
        self.event_name_label.setWordWrap(True)
        self.event_name_label.setMinimumHeight(80)
        self.event_name_label.setTextFormat(Qt.TextFormat.RichText)
        details_layout.addWidget(self.event_name_label)
        
        details_hbox = QHBoxLayout()
        
        self.location_check = QCheckBox("Địa điểm")
        self.location_check.setEnabled(False)
        details_hbox.addWidget(self.location_check)
        
        self.reminder_check = QCheckBox("Nhắc trước")
        self.reminder_check.setEnabled(False)
        details_hbox.addWidget(self.reminder_check)
        
        details_hbox.addStretch()
        details_layout.addLayout(details_hbox)
        details_group.setLayout(details_layout)
        bottom_layout.addWidget(details_group, 2)  # Chiếm 2 phần
        
        # Sửa xóa
        action_group = QGroupBox("Thao tác")
        action_layout = QVBoxLayout()
        
        edit_button = QPushButton("Sửa")
        edit_button.clicked.connect(self.edit_event)
        edit_button.setMinimumHeight(40)
        action_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Xóa")
        delete_button.clicked.connect(self.delete_event)
        delete_button.setMinimumHeight(40)
        action_layout.addWidget(delete_button)
        
        # Xuất/Nhập file json
        file_layout = QHBoxLayout()
        export_button = QPushButton("Xuất")
        export_button.clicked.connect(self.export_events)
        file_layout.addWidget(export_button)
        
        import_button = QPushButton("Nhập")
        import_button.clicked.connect(self.import_events)
        file_layout.addWidget(import_button)
        
        action_layout.addLayout(file_layout)
        action_group.setLayout(action_layout)
        bottom_layout.addWidget(action_group, 1)
        
        main_layout.addLayout(bottom_layout)
        
        # Status bar
        self.statusBar().showMessage(f"Sẵn sàng • {len(self.db.get_all_events())} sự kiện")
        
        # Connect table selection
        self.events_table.itemSelectionChanged.connect(self.on_event_selected)
        
        # Biến để theo dõi trạng thái tìm kiếm
        self.is_searching = False
        self.search_results = []
    
    def get_date_range_text(self) -> str:
        """Get text representation of current date range."""
        if self.current_view == "day":
            return self.current_date.strftime("%d/%m/%Y")
        elif self.current_view == "week":
            # Find Monday of the week
            monday = self.current_date - timedelta(days=self.current_date.weekday())
            sunday = monday + timedelta(days=6)
            return f"{monday.strftime('%d/%m')} - {sunday.strftime('%d/%m/%Y')}"
        else:  # month
            return self.current_date.strftime("%m/%Y")
    
    def load_events(self):
        """Load events based on current view."""
        events = []
        
        if self.current_view == "day":
            events = self.db.get_events_by_date(self.current_date)
        elif self.current_view == "week":
            events = self.db.get_events_by_week(self.current_date)
        else:  # month
            events = self.db.get_events_by_month(
                self.current_date.year, 
                self.current_date.month
            )
        
        self.current_events = events  # Lưu trữ cho tìm kiếm
        self.display_events(events)
        
        # Update status
        total_events = len(self.db.get_all_events())
        if self.is_searching:
            self.statusBar().showMessage(
                f"Đang tìm kiếm • Hiển thị {len(events)}/{total_events} sự kiện"
            )
        else:
            self.statusBar().showMessage(
                f"Hiển thị {len(events)}/{total_events} sự kiện • {self.get_date_range_text()}"
            )
    
    def display_events(self, events: list):
        """Display events in table."""
        self.events_table.setRowCount(len(events))
        
        for row, event in enumerate(events):
            # Ngày
            date_item = QTableWidgetItem(event.start_time.strftime("%d/%m/%Y"))
            date_item.setData(Qt.ItemDataRole.UserRole, event.id)
            date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.events_table.setItem(row, 0, date_item)
            
            # Thời gian
            time_item = QTableWidgetItem(event.start_time.strftime("%H:%M"))
            time_item.setFlags(time_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.events_table.setItem(row, 1, time_item)
            
            # Địa điểm
            location_text = event.location if event.location else ""
            location_item = QTableWidgetItem(location_text)
            location_item.setFlags(location_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.events_table.setItem(row, 2, location_item)
            
            # Sự kiện
            name_item = QTableWidgetItem(event.event_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.events_table.setItem(row, 3, name_item)
    
    def on_event_selected(self):
        """When an event is selected in the table."""
        selected_items = self.events_table.selectedItems()
        
        if not selected_items:
            self.event_name_label.setText("Chọn một sự kiện để xem chi tiết")
            self.location_check.setChecked(False)
            self.reminder_check.setChecked(False)
            return
        
        # Get event ID from first column
        row = selected_items[0].row()
        event_id_item = self.events_table.item(row, 0)
        event_id = event_id_item.data(Qt.ItemDataRole.UserRole)
        
        # Get event from database
        event = self.db.get_event(event_id)
        
        if event:
            # Display event details with better formatting
            time_str = event.start_time.strftime("%H:%M %d/%m/%Y")
            
            # Create HTML for better display
            details_html = f"""
            <div style='font-size: 12pt;'>
            <b>Event {event.event_name}</b><br>
            <span style='color: #555;'>Time {time_str}</span>
            """
            
            if event.location:
                details_html += f"<br><span style='color: #555;'>Location {event.location}</span>"
            
            if event.reminder_minutes > 0:
                details_html += f"<br><span style='color: #555;'> Remind {event.reminder_minutes} phút</span>"
            
            details_html += "</div>"
            
            self.event_name_label.setText(details_html)
            
            # Location check
            self.location_check.setChecked(event.location is not None)
            
            # Reminder check
            self.reminder_check.setChecked(event.reminder_minutes > 0)
        else:
            self.event_name_label.setText("Không tìm thấy thông tin sự kiện")
            self.location_check.setChecked(False)
            self.reminder_check.setChecked(False)
    
    # === PHẦN TÌM KIẾM MỚI ===
    def search_events(self):
        """Tìm kiếm sự kiện theo từ khóa."""
        keyword = self.search_input.text().strip()
        
        if not keyword:
            QMessageBox.warning(self, "Vui lòng nhập từ khóa tìm kiếm!")
            return
        
        # Thực hiện tìm kiếm
        search_results = self.db.search_events(keyword)
        self.search_results = search_results  # Lưu kết quả tìm kiếm
        
        # Hiển thị kết quả
        self.display_search_results(search_results, keyword)
    
    def display_search_results(self, events: list, keyword: str):
        """Hiển thị kết quả tìm kiếm."""
        if not events:
            QMessageBox.information(
                self, 
                "Không tìm thấy", 
                f"Không tìm thấy sự kiện nào với từ khóa '{keyword}'"
            )
            return
        
        # Hiển thị trong bảng
        self.display_events(events)
        
        # Cập nhật trạng thái
        self.is_searching = True
        
        # Cập nhật status bar
        self.statusBar().showMessage(
            f"Tìm kiếm: '{keyword}' • Tìm thấy {len(events)} sự kiện"
        )
    
    def clear_search(self):
        """Xóa kết quả tìm kiếm và quay lại chế độ xem bình thường."""
        self.search_input.clear()
        self.is_searching = False
        self.search_results = []
        
        # Tải lại sự kiện theo chế độ xem hiện tại
        self.load_events()
        
        # Cập nhật status bar
        total_events = len(self.db.get_all_events())
        self.statusBar().showMessage(
            f"Hiển thị {len(self.current_events)}/{total_events} sự kiện • {self.get_date_range_text()}"
        )

    
    def add_event_nlp(self):
        """Add event using NLP input."""
        text = self.nlp_input.text().strip()
        
        if not text:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập mô tả sự kiện!")
            return
        
        try:
            # Parse NLP text
            event = self.nlp_processor.parse_text(text)
            
            if not event:
                QMessageBox.warning(self, "Lỗi phân tích", "Không thể phân tích câu của bạn. Vui lòng thử lại!")
                return
            
            # Add to database
            event_id = self.db.add_event(event)
            
            if event_id:
                self.nlp_input.clear()
                
                # Nếu đang trong chế độ tìm kiếm, xóa tìm kiếm
                if self.is_searching:
                    self.clear_search()
                else:
                    self.load_events()
                
                # Show success message
                event_time = event.start_time.strftime("%H:%M %d/%m")
                location_info = f"\nĐịa điểm: {event.location}" if event.location else ""
                QMessageBox.information(
                    self, 
                    "Thành công", 
                    f"Đã thêm sự kiện: {event.event_name}\nLúc: {event_time}{location_info}"
                )
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể thêm sự kiện!")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def edit_event(self):
        """Edit selected event."""
        selected_items = self.events_table.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một sự kiện để sửa!")
            return
        
        # Get event ID
        row = selected_items[0].row()
        event_id_item = self.events_table.item(row, 0)
        event_id = event_id_item.data(Qt.ItemDataRole.UserRole)
        
        # Get current event
        current_event = self.db.get_event(event_id)
        if current_event:
            # Create pre-filled text
            time_str = current_event.start_time.strftime("%H:%M")
            prefilled = f"{current_event.event_name} lúc {time_str}"
            if current_event.location:
                prefilled += f" ở {current_event.location}"
        else:
            prefilled = ""
        
        # Ask for new text
        text, ok = QInputDialog.getText(
            self,
            "Sửa sự kiện",
            "Nhập mô tả mới cho sự kiện:",
            QLineEdit.EchoMode.Normal,
            prefilled
        )
        
        if ok and text:
            try:
                # Parse new text
                new_event = self.nlp_processor.parse_text(text)
                
                if not new_event:
                    QMessageBox.warning(self, "Lỗi", "Không thể phân tích câu!")
                    return
                
                # Update event ID
                new_event.id = event_id
                new_event.updated_at = datetime.now()
                
                # Update in database
                success = self.db.update_event(new_event)
                
                if success:
                    # Nếu đang trong chế độ tìm kiếm, cập nhật kết quả tìm kiếm
                    if self.is_searching and self.search_input.text().strip():
                        self.search_events()
                    else:
                        self.load_events()
                    QMessageBox.information(self, "Thành công", "Đã cập nhật sự kiện!")
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể cập nhật!")
                    
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Có lỗi: {str(e)}")
    
    def delete_event(self):
        """Delete selected event."""
        selected_items = self.events_table.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Chưa chọn", "Vui lòng chọn một sự kiện để xóa!")
            return
        
        # Get event details
        row = selected_items[0].row()
        event_name = self.events_table.item(row, 3).text()
        event_id_item = self.events_table.item(row, 0)
        event_id = event_id_item.data(Qt.ItemDataRole.UserRole)
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa sự kiện:\n'{event_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.db.delete_event(event_id)
            
            if success:
                # Nếu đang trong chế độ tìm kiếm, cập nhật kết quả tìm kiếm
                if self.is_searching and self.search_input.text().strip():
                    self.search_events()
                else:
                    self.load_events()
                QMessageBox.information(self, "Thành công", "Đã xóa sự kiện!")
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể xóa sự kiện!")
    
    def change_view(self):
        """Change view mode based on radio buttons."""
        if self.day_radio.isChecked():
            self.current_view = "day"
        elif self.week_radio.isChecked():
            self.current_view = "week"
        else:
            self.current_view = "month"
        
        # Nếu đang tìm kiếm, xóa tìm kiếm
        if self.is_searching:
            self.clear_search()
        else:
            self.date_label.setText(self.get_date_range_text())
            self.load_events()
    
    def prev_period(self):
        """Go to previous period."""
        if self.current_view == "day":
            self.current_date -= timedelta(days=1)
        elif self.current_view == "week":
            self.current_date -= timedelta(weeks=1)
        else:  # month
            if self.current_date.month == 1:
                self.current_date = date(self.current_date.year - 1, 12, 1)
            else:
                self.current_date = date(self.current_date.year, self.current_date.month - 1, 1)
        
        # Nếu đang tìm kiếm, xóa tìm kiếm
        if self.is_searching:
            self.clear_search()
        else:
            self.date_label.setText(self.get_date_range_text())
            self.load_events()
    
    def next_period(self):
        """Go to next period."""
        if self.current_view == "day":
            self.current_date += timedelta(days=1)
        elif self.current_view == "week":
            self.current_date += timedelta(weeks=1)
        else:  # month
            if self.current_date.month == 12:
                self.current_date = date(self.current_date.year + 1, 1, 1)
            else:
                self.current_date = date(self.current_date.year, self.current_date.month + 1, 1)
        
        # Nếu đang tìm kiếm, xóa tìm kiếm
        if self.is_searching:
            self.clear_search()
        else:
            self.date_label.setText(self.get_date_range_text())
            self.load_events()
    
    def go_to_today(self):
        """Go to today."""
        self.current_date = date.today()
        
        # Nếu đang tìm kiếm, xóa tìm kiếm
        if self.is_searching:
            self.clear_search()
        else:
            self.date_label.setText(self.get_date_range_text())
            self.load_events()
    
    def export_events(self):
        """Export events to JSON."""
        events = []
        
        # Nếu đang tìm kiếm, xuất kết quả tìm kiếm
        if self.is_searching and self.search_results:
            events = self.search_results
        else:
            events = self.db.get_all_events()
        
        if not events:
            QMessageBox.warning(self, "Không có dữ liệu", "Không có sự kiện nào để xuất!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Xuất sự kiện",
            f"schedule_{datetime.now().strftime('%d%m%Y_%H%M')}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            success = self.file_handler.export_to_json(events, filename)
            
            if success:
                QMessageBox.information(
                    self,
                    "Xuất thành công",
                    f"Đã xuất {len(events)} sự kiện ra file!"
                )
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể xuất file!")
    
    def import_events(self):
        """Import events from JSON."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Nhập sự kiện",
            "",
            "JSON Files (*.json)"
        )
        
        if filename:
            reply = QMessageBox.question(
                self,
                "Xác nhận nhập",
                "Nhập sự kiện từ file này?\n(Lưu ý: Sự kiện trùng thời gian có thể bị ghi đè)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success_count, total_count, errors = self.file_handler.import_from_json(filename, self.db)
                
                if success_count > 0:
                    # Nếu đang tìm kiếm, xóa tìm kiếm
                    if self.is_searching:
                        self.clear_search()
                    else:
                        self.load_events()
                
                if errors:
                    error_msg = "\n".join(errors[:3])
                    if len(errors) > 3:
                        error_msg += f"\n...và {len(errors)-3} lỗi khác"
                    
                    QMessageBox.warning(
                        self,
                        f"Nhập hoàn tất ({success_count}/{total_count})",
                        f"Có một số lỗi:\n{error_msg}"
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Thành công",
                        f"Đã nhập {success_count} sự kiện!"
                    )
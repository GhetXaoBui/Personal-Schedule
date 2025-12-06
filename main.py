#!/usr/bin/env python3
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from main_window import MainWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Personal Schedule Assistant")
    app.setStyle("Fusion")
    
    # Create exports directory
    os.makedirs("exports", exist_ok=True)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
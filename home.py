import os
import sys
import subprocess
from configparser import ConfigParser
from pathlib import Path
from PyQt5.QtCore import Qt, QCoreApplication, QThread, pyqtSignal, QSize, pyqtSlot, QEvent
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QVBoxLayout, QWidget, QToolButton, QScrollArea, QFrame, QGridLayout,
    QDesktopWidget, QPushButton
)
from PyQt5.QtGui import QIcon

from pynput.keyboard import Key, Listener

center_width = 7


class KeyboardListener(QThread):
    key_pressed = pyqtSignal(object)

    def run(self):
        with Listener(on_press=self.on_key_press) as listener:
            listener.join()

    def on_key_press(self, key):
        self.key_pressed.emit(key)


# noinspection PyUnresolvedReferences
class AppLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        # Track selector
        self.selected_index = 0

        self.setWindowTitle("App Launcher")
        self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setGeometry(QDesktopWidget().availableGeometry())
        self.setStyleSheet("background-color: rgba(50, 50, 50, 150);")  # Adjust the alpha value as needed
        self.is_front = False

        self.app_suggestions = self.discover_installed_apps()
        self.filtered_apps = self.app_suggestions

        # Keyboard listener
        self.setup_keyboard_listener()
        self.start_keyboard_listener()

        self.create_ui()


    # UI
    def create_ui(self):
        self.create_search_bar()
        self.create_app_grid()

    def create_search_bar(self):
        self.search_var = QLineEdit(self)
        self.search_var.setPlaceholderText("Search for applications...")
        self.search_var.setStyleSheet(
            "QLineEdit {"
            "   background-color: rgba(104, 255, 200, 200);"
            "   border-radius: 30px;"
            "   padding: 15px 30px 15px 30px;"
            "   font-size: 24px;"
            "   color: rgb(218, 214, 247);"
            "}"
        )

        self.search_var.setFixedWidth(center_width * 105)

        search_layout = QVBoxLayout()
        search_layout.addWidget(self.search_var, alignment=Qt.AlignTop | Qt.AlignHCenter)

        search_widget = QWidget(self)
        search_widget.setLayout(search_layout)

        self.setCentralWidget(search_widget)

    def create_app_grid(self):
        self.app_grid_widget = QWidget(self)
        self.app_grid_layout = QGridLayout(self.app_grid_widget)
        self.app_grid_layout.setAlignment(Qt.AlignTop)
        self.app_grid_widget.setLayout(self.app_grid_layout)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.app_grid_widget)
        scroll_area.setStyleSheet("background: transparent; border: 0px;")

        scroll_bar = scroll_area.verticalScrollBar()
        scroll_bar.setStyleSheet("QScrollBar:vertical { width: 0; }")

        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setFixedWidth(center_width * 100)

        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(self.search_var, alignment=Qt.AlignTop | Qt.AlignHCenter)
        main_layout.addWidget(scroll_area, alignment=Qt.AlignHCenter)
        self.setCentralWidget(main_widget)

        self.update_app_grid()
        self.search_var.textChanged.connect(self.text_updated)

        # Connect arrow key signals to methods
        self.search_var.installEventFilter(self)

    def text_updated(self):
        self.selected_index = 0
        self.update_app_grid()

    def update_app_grid(self):
        self.app_grid_layout.setSpacing(32)

        for i in reversed(range(self.app_grid_layout.count())):
            self.app_grid_layout.itemAt(i).widget().setParent(None)

        search_text = self.search_var.text().lower()

        self.filtered_apps = [app_info for app_info in self.app_suggestions if search_text in app_info['name'].lower()]

        row, col = 0, 0
        for i, app_info in enumerate(self.filtered_apps):
            app_button = QToolButton(self)
            icon_name = app_info['icon']
            app_button.setIcon(QIcon.fromTheme(icon_name))
            app_button.setIconSize(QSize(64, 64))
            app_button.setStyleSheet(
                "QToolTip {"
                "   color: #ffffff;"
                "   background-color: rgba(0, 0, 0, 200);"
                "   border: 1px solid #ffffff;"
                "   border-radius: 2px;"
                "}"
                "QToolButton {"
                "   background-color: rgba(104, 255, 200, 150);"
                "   border-radius: 5px;"
                "}"
            )

            # Highlight the selected app
            if i == self.selected_index:
                app_button.setStyleSheet(
                    app_button.styleSheet() + "QToolButton { border: 2px solid red; }"
                )
            else:
                app_button.setStyleSheet(
                    app_button.styleSheet() + "QToolButton { border: 2px solid rgba(104, 255, 200, 200); }"
                )
            app_button.setToolTip(app_info['name'])
            app_button.clicked.connect(lambda _, exe=app_info['executable']: self.launch_and_hide(exe))
            self.app_grid_layout.addWidget(app_button, row, col, alignment=Qt.AlignCenter)
            col += 1
            if col >= center_width:
                col = 0
                row += 1

    def eventFilter(self, obj, event):
        # The external thread cannot be used because the text box eats the input normally
        if obj == self.search_var and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Right:
                self.selected_index += 1
            elif event.key() == Qt.Key_Left:
                self.selected_index -= 1
            elif event.key() == Qt.Key_Up:
                self.selected_index -= center_width
            elif event.key() == Qt.Key_Down:
                self.selected_index += center_width
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                try:
                    app_info = self.filtered_apps[self.selected_index]
                    exe = app_info['executable']
                    self.launch_and_hide(exe)
                except IndexError:
                    pass
            elif event.key() == Qt.Key_Escape:
                self.hide_application()
            if self.selected_index >= len(self.filtered_apps):
                self.selected_index = len(self.filtered_apps) - 1
            elif self.selected_index < 0:
                # TODO: Implement web search suggestions above search bar
                self.selected_index = 0
            self.update_app_grid()
        return super().eventFilter(obj, event)

    # Internal functionality
    def discover_installed_apps(self):
        installed_apps = []

        desktop_dirs = [
            '/usr/share/applications/',
            str(Path.home()) + '/.local/share/applications/',
	        str(Path.home()) + '/Desktop/'
        ]

        for desktop_dir in desktop_dirs:
            if not os.path.exists(desktop_dir):
                continue

            for desktop_file in os.listdir(desktop_dir):
                if desktop_file.endswith('.desktop'):
                    app_info = self.parse_desktop_file(os.path.join(desktop_dir, desktop_file))
                    if app_info:
                        installed_apps.append(app_info)

        return installed_apps

    def parse_desktop_file(self, file_path):
        config = ConfigParser(interpolation=None)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                config.read_file(file)
        except Exception as e:
            return None

        if 'Desktop Entry' in config:
            app_info = {
                'name': config['Desktop Entry'].get('Name', ''),
                'executable': config['Desktop Entry'].get('Exec', ''),
                'icon': config['Desktop Entry'].get('Icon', '')
            }
            return app_info
        else:
            return None

    def launch_and_hide(self, executable_command):
        try:
            subprocess.Popen(executable_command, shell=True)
        except Exception as e:
            print(f"Error: Failed to launch application. Exception: {e}")

        self.hide_application()

    def setup_keyboard_listener(self):
        self.keyboard_listener = KeyboardListener()
        self.keyboard_listener.key_pressed.connect(self.on_key_pressed)

    def start_keyboard_listener(self):
        self.keyboard_listener.start()

    @pyqtSlot(object)
    def on_key_pressed(self, key):
        if key == Key.cmd:
            if self.is_front:
                self.hide_application()
            else:
                self.show_application()

    def hide_application(self):
        self.hide()
        self.selected_index = 0
        self.search_var.clear()
        self.is_front = False

    def show_application(self):
        self.show()
        self.search_var.clear()
        self.app_suggestions = self.discover_installed_apps()
        QCoreApplication.processEvents()

        self.raise_()
        self.activateWindow()

        self.search_var.setFocus()
        self.is_front = True

    def closeEvent(self, event):
        try:
            self.stop_keyboard_listener()
            self.keyboard_listener.wait()
        finally:
            event.accept()

    def stop_keyboard_listener(self):
        if self.keyboard_listener.isRunning():
            self.keyboard_listener.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppLauncher()
    sys.exit(app.exec_())

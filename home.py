import os
import sys
import subprocess
from configparser import ConfigParser
from pathlib import Path
from PyQt5.QtCore import Qt, QCoreApplication, QThread, pyqtSignal, QSize, pyqtSlot, QEvent, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QWidget, QToolButton, QScrollArea, \
    QFrame, QGridLayout, QDesktopWidget
from PyQt5.QtGui import QIcon
from pynput.keyboard import Key, Listener

# TODO: Move constants like 'center_width' to a separate configuration file or class for better organization.
grid_width = 7


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App Launcher")
        self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setGeometry(QDesktopWidget().availableGeometry())
        self.setStyleSheet("background-color: rgba(56, 60, 74, 150);")  # Adjust the alpha value as needed
        self.is_front = False
        
        self.create_ui()
    
    def create_ui(self):
        self.create_search_bar()
        self.create_app_grid()
    
    def create_search_bar(self):
        self.search_var = QLineEdit(self)
        self.search_var.setFixedWidth(grid_width * 100)
        self.search_var.setPlaceholderText("Search for applications...")
        self.search_var.setStyleSheet(
            "QLineEdit {"
            "   background-color: rgba(129, 161, 193, 200);"
            "   border-radius: 27px;"
            "   padding: 15px 30px 15px 30px;"
            "   font-size: 24px;"
            "   color: rgb(229, 233, 240);"
            "}"
        )
        
        # TODO: Consider using a separate method for layout setup to reduce complexity of this method.
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
        
        # TODO: Encapsulate scroll area setup into a separate method for better organization.
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.app_grid_widget)
        scroll_area.setStyleSheet("background: transparent; border: 0px;")
        
        scroll_bar = scroll_area.verticalScrollBar()
        scroll_bar.setStyleSheet("QScrollBar:vertical { width: 0; }")
        
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setFixedWidth(grid_width * 100)
        
        # TODO: Refactor this widget setup into a method to reduce method length and improve readability.
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(self.search_var, alignment=Qt.AlignTop | Qt.AlignHCenter)
        main_layout.addWidget(scroll_area, alignment=Qt.AlignHCenter)
        self.setCentralWidget(main_widget)
        
        self.app_grid_layout.setSpacing(32)
        
        self.search_var.textChanged.connect(appLauncher.text_updated)
        self.search_var.installEventFilter(self)
    
    def add_app(self, name, icon, cmd, row, col, selected):
        app_button = QToolButton(self)
        icon_name = icon
        app_button.setIcon(QIcon.fromTheme(icon_name))
        app_button.setIconSize(QSize(64, 64))
        app_button.setStyleSheet(
            "QToolTip {"
            "   color: #ffffff;"
            "   background-color: rgba(56, 60, 74, 200);"
            "   border: 1px solid #ffffff;"
            "   border-radius: 2px;"
            "}"
            "QToolButton {"
            "   background-color: rgba(76, 86, 106, 150);"
            "   border-radius: 5px;"
            "}"
        )
        
        if selected:
            app_button.setStyleSheet(
                app_button.styleSheet() + "QToolButton { border: 2px solid rgb(229, 233, 240); }")
        else:
            app_button.setStyleSheet(
                app_button.styleSheet() + "QToolButton { border: 2px solid rgba(129, 161, 193, 200); }")
        app_button.setToolTip(name)
        app_button.clicked.connect(lambda _, exe=cmd: self.launch_and_hide(exe))
        self.app_grid_layout.addWidget(app_button, row, col, alignment=Qt.AlignCenter)
    
    # GUI navigation
    def eventFilter(self, obj, event):
        # The external thread cannot be used because the text box eats the input normally
        if obj == self.search_var and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Right:
                appLauncher.selected_index += 1
            elif event.key() == Qt.Key_Left:
                appLauncher.selected_index -= 1
            elif event.key() == Qt.Key_Up:
                appLauncher.selected_index -= grid_width
            elif event.key() == Qt.Key_Down:
                appLauncher.selected_index += grid_width
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                try:
                    app_info = appLauncher.filtered_apps[appLauncher.selected_index]
                    exe = app_info['executable']
                    appLauncher.launch_and_hide(exe)
                except IndexError:
                    pass
            elif event.key() == Qt.Key_Escape:
                self.hide_app()
            if appLauncher.selected_index >= len(appLauncher.filtered_apps):
                appLauncher.selected_index = len(appLauncher.filtered_apps) - 1
            elif appLauncher.selected_index < 0:
                # TODO: Implement web search suggestions above search bar
                appLauncher.selected_index = 0
            appLauncher.update_app_grid()
        return super().eventFilter(obj, event)
    
    def hide_app(self):
        self.hide()
        appLauncher.selected_index = 0
        self.search_var.clear()
        self.is_front = False
    
    def show_app(self):
        print(0)
        window.show()
        window.search_var.clear()
        appLauncher.app_suggestions = appLauncher.discover_installed_apps()
        QCoreApplication.processEvents()
        
        window.raise_()
        window.activateWindow()
        window.search_var.setFocus()
        window.is_front = True
        
        appLauncher.update_app_grid()


class AppLauncher():
    def __init__(self):
        self.app_suggestions = self.discover_installed_apps()
        self.filtered_apps = self.app_suggestions
        self.selected_index = 0
    
    def text_updated(self):
        self.selected_index = 0
        self.update_app_grid()
    
    def discover_installed_apps(self):
        installed_apps = []
        # TODO: user customization for this option
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
            # TODO: Log this error instead of silently failing, perhaps using Python's logging module.
            return None
        
        if 'Desktop Entry' in config:
            return {
                'name': config['Desktop Entry'].get('Name', ''),
                'executable': config['Desktop Entry'].get('Exec', ''),
                'icon': config['Desktop Entry'].get('Icon', '')
            }
        return None
    
    def search_apps(self):
        for i in reversed(range(window.app_grid_layout.count())):
            window.app_grid_layout.itemAt(i).widget().setParent(None)
        
        search_text = window.search_var.text().lower()
        self.filtered_apps = [app_info for app_info in self.app_suggestions if search_text in app_info['name'].lower()]
    
    def update_app_grid(self):
        self.search_apps()
        row, col = 0, 0
        for i, app_info in enumerate(self.filtered_apps):
            if i == self.selected_index:
                selected = True
            else:
                selected = False
            name = app_info['name']
            icon = app_info['icon']
            cmd = app_info['executable']
            window.add_app(name, icon, cmd, row, col, selected)
            
            col += 1
            if col >= grid_width:
                col = 0
                row += 1
    
    def launch_and_hide(self, executable_command):
        try:
            subprocess.Popen(executable_command, shell=True)
        except Exception as e:
            # TODO: Implement better error handling, possibly with user notification.
            print(f"Error: Failed to launch application. Exception: {e}")
        window.hide_app()


class KeyboardListenerThread(QThread):
    key_pressed = pyqtSignal(object)
    
    def run(self):
        with Listener(on_press=self.on_key_press) as listener:
            listener.join()
    
    def on_key_press(self, key):
        self.key_pressed.emit(key)


class KeyboardListenerLogic(QObject):
    def __init__(self):
        super().__init__()
        self.keyboard_listener = KeyboardListenerThread()
        self.keyboard_listener.key_pressed.connect(self.on_key_pressed)
        self.keyboard_listener.start()
    
    @pyqtSlot(object)
    def on_key_pressed(self, key):
        if key == Key.cmd:
            if window.is_front:
                window.hide_app()
            else:
                window.show_app()
    
    def close_event(self, event):
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
    appLauncher = AppLauncher()
    window = GUI()
    listener = KeyboardListenerLogic()
    sys.exit(app.exec_())

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QScrollArea, QWidget, QScrollBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeyEvent

from .image_handler import ImageHandler, ImageHandlerSingle
from .folder_image_reader import FolderImageReader
from .toolbar import MainToolBar


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()  # 繼承 QMainWindow 並呼叫其建構子

        # 初始化 FolderImageReader、ImageHandler 和 ImageHandlerSingle 物件
        self.image_reader = FolderImageReader()
        self.image_handler = ImageHandler()
        self.image_handler_single = ImageHandlerSingle()

        self.image_reader.set_callback(self.folder_clicked)  # 設定回調函數

        self.initUI()  # 執行 initUI 方法來設定使用者介面

        self.toolbar.open_folder()  # 開啟工具列預設資料夾
        self.active_module = 'folder_image_reader'  # 默認為多頁模式
        QTimer.singleShot(50, self.image_reader.adjust_layout)

    def initUI(self):
        # 設定視窗標題和大小
        self.setWindowTitle('圖片瀏覽器')
        self.setGeometry(100, 100, 800, 1000)
        self.showMaximized()                   # 設置視窗最大化顯示

        # 建立工具列並加入主視窗
        self.toolbar = MainToolBar(self)
        self.addToolBar(self.toolbar)

        # 建立主佈局並添加可滾動區域
        main_layout = QVBoxLayout()

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.verticalScrollBar().setSingleStep(800)
        main_layout.addWidget(self.scrollArea)

        # 設定中央小部件並添加佈局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key_F5:
            self.init_active_module("folder_image_reader")
            self.image_reader.adjust_layout()

        if self.active_module == 'folder_image_reader':
            navigation_map = {
                Qt.Key_W: lambda: self.image_reader.select_item('col', 'previous'),
                Qt.Key_Up: lambda: self.image_reader.select_item('col', 'previous'),
                Qt.Key_S: lambda: self.image_reader.select_item('col', 'next'),
                Qt.Key_Down: lambda: self.image_reader.select_item('col', 'next'),
                Qt.Key_A: lambda: self.image_reader.select_item('row', 'previous'),
                Qt.Key_Left: lambda: self.image_reader.select_item('row', 'previous'),
                Qt.Key_D: lambda: self.image_reader.select_item('row', 'next'),
                Qt.Key_Right: lambda: self.image_reader.select_item('row', 'next'),
                Qt.Key_Return: lambda: self.image_reader.select_current_item(),
                Qt.Key_O: lambda: self.toolbar.open_folder(),
                Qt.Key_F: lambda: self.image_reader.load_images(load_all=True)
            }
            if key in navigation_map:
                navigation_map[key]()

        elif self.active_module in ['multi', 'single']:
            scroll_map = {
                Qt.Key_W: QScrollBar.SliderSingleStepSub,
                Qt.Key_Space: QScrollBar.SliderSingleStepAdd,
                Qt.Key_S: QScrollBar.SliderSingleStepAdd,
            }

            # 检查 Ctrl 修饰键，并应用于 multi 和 single 模式
            if modifiers == Qt.ControlModifier:
                if key == Qt.Key_W:
                    zoom_func = self.image_handler.zoom if self.active_module == 'multi' else self.image_handler_single.zoom
                    zoom_func(1.25)  # 放大
                elif key == Qt.Key_S:
                    zoom_func = self.image_handler.zoom if self.active_module == 'multi' else self.image_handler_single.zoom
                    zoom_func(0.8)  # 缩小
            elif key in scroll_map:
                self.scrollArea.verticalScrollBar(
                ).triggerAction(scroll_map[key])
            elif key == Qt.Key_Escape:
                self.toolbar.go_back()
            elif self.active_module == 'single':
                if key == Qt.Key_D:
                    self.image_handler_single.next_image(self.scrollArea)
                elif key == Qt.Key_A:
                    self.image_handler_single.previous_image(self.scrollArea)

        super().keyPressEvent(event)

    def init_active_module(self, flag):
        self.active_module = flag
        self.image_reader.active_module = flag
        self.image_handler.active_module = flag
        self.image_handler_single.active_module = flag

    def switch_mode(self, mode, folder_path):
        if mode in ['multi', 'single']:
            self.init_active_module(mode)
            self.display_images(folder_path)

    def display_images(self, folder_path):
        if self.active_module == 'multi':
            self.image_handler.load_images(folder_path)
            self.image_handler.display_images(self.scrollArea)
        elif self.active_module == 'single':
            self.image_handler_single.load_images(folder_path)
            self.image_handler_single.display_images(self.scrollArea)

    def display_folders(self, folder_path):
        self.init_active_module('folder_image_reader')
        self.image_reader.display_folders(folder_path, self.scrollArea)

    def folder_clicked(self, folder_path):
        self.toolbar.folder_clicked_log(folder_path)
        self.init_active_module('multi')
        self.display_images(folder_path)

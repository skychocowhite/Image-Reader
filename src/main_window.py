from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QScrollArea, QWidget, QScrollBar, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeyEvent

from .reader_mode import ViewerMode, ViewerStatus
from .image_handlers.image_handler import ImageHandler
from .image_handlers.image_handler_multi import ImageHandlerMulti
from .image_handlers.image_handler_single import ImageHandlerSingle
from .folder_image_reader import FolderImageReader
from .toolbar import MainToolBar


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()  # 繼承 QMainWindow 並呼叫其建構子

        # 初始化 FolderImageReader、ImageHandler 物件
        self.image_reader = FolderImageReader()
        self.image_handler: ImageHandler = ImageHandlerMulti()

        self.image_reader.set_callback(self.folder_clicked)  # 設定回調函數

        self.initUI()  # 執行 initUI 方法來設定使用者介面

        self.openFolder()  # 開啟工具列預設資料夾
        ViewerStatus.current_mode = ViewerMode.FOLDER_IMAGE
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
        self.scrollArea.verticalScrollBar().valueChanged.connect(
            lambda: self.image_handler.on_scroll(self.scrollArea))
        main_layout.addWidget(self.scrollArea)

        # 設定中央小部件並添加佈局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key_F5:
            ViewerStatus.current_mode = ViewerMode.FOLDER_IMAGE
            self.image_reader.adjust_layout()

        # Direction key not working
        if ViewerStatus.current_mode == ViewerMode.FOLDER_IMAGE:
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
                Qt.Key_O: lambda: self.openFolder(),
                Qt.Key_F: lambda: self.image_reader.load_images(load_all=True)
            }
            if key in navigation_map:
                navigation_map[key]()

        elif ViewerStatus.current_mode in [ViewerMode.MULTI_PAGE, ViewerMode.SINGLE_PAGE]:
            scroll_map = {
                Qt.Key_W: QScrollBar.SliderSingleStepSub,
                Qt.Key_Space: QScrollBar.SliderSingleStepAdd,
                Qt.Key_S: QScrollBar.SliderSingleStepAdd,
            }

            # 检查 Ctrl 修饰键，并应用于 multi 和 single 模式
            if modifiers == Qt.ControlModifier:
                if key == Qt.Key_W:
                    self.image_handler.zoom(1.25)  # 放大
                elif key == Qt.Key_S:
                    self.image_handler.zoom(0.8)   # 縮小
            elif key in scroll_map:
                self.scrollArea.verticalScrollBar(
                ).triggerAction(scroll_map[key])
            elif key == Qt.Key_Escape:
                self.toolbar.go_back()
            elif key == Qt.Key_D:
                self.image_handler.next_image(self.scrollArea)
            elif key == Qt.Key_A:
                self.image_handler.previous_image(self.scrollArea)

        super().keyPressEvent(event)

    def switch_mode(self, mode, folder_path):
        if mode == ViewerMode.MULTI_PAGE:
            self.image_handler = ImageHandlerMulti()
        elif mode == ViewerMode.SINGLE_PAGE:
            self.image_handler = ImageHandlerSingle()

        ViewerStatus.current_mode = mode
        self.display_images(folder_path)

    def display_images(self, folder_path):
        self.image_handler.load_images(folder_path)
        self.image_handler.display_images(self.scrollArea)

    def display_folders(self, folder_path):
        ViewerStatus.current_mode = ViewerMode.FOLDER_IMAGE
        self.image_reader.display_folders(folder_path, self.scrollArea)

    def openFolder(self, folder_path=None):
        """Open folder from file explorer"""

        # Check if the folder path is given
        if folder_path is None:
            folder_path = QFileDialog.getExistingDirectory(self, "打開資料夾", "")

        # Open files given the folder path
        if folder_path:
            self.toolbar.changeFolder(folder_path)
            self.display_folders(folder_path)

    def folder_clicked(self, folder_path):
        self.toolbar.folder_clicked_log(folder_path)
        ViewerStatus.current_mode = ViewerMode.MULTI_PAGE
        self.display_images(folder_path)

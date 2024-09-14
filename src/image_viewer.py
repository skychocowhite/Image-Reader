from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QScrollArea, QWidget, QFileDialog
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QKeyEvent

from .reader_mode import ViewerMode
from .image_handlers.image_handler import ImageHandler
from .image_handlers.image_handler_multi import ImageHandlerMulti
from .image_handlers.image_handler_single import ImageHandlerSingle
from .folder_image_reader import FolderImageReader
from .toolbar import MainToolBar
from .modes.mode import Mode
from .modes.folder_image_mode import FolderImageMode
from .modes.image_multi_mode import MultiImageMode
from .modes.image_single_mode import SingleImageMode


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()  # 繼承 QMainWindow 並呼叫其建構子

        # 初始化 FolderImageReader、ImageHandler 物件
        self.image_reader = FolderImageReader()
        self.image_handler: ImageHandler = ImageHandlerMulti()

        self.image_reader.set_callback(self.folder_clicked)  # 設定回調函數
        self.mode: Mode = None

        self.set_mode(ViewerMode.FOLDER_IMAGE)
        self.initUI()  # 執行 initUI 方法來設定使用者介面
        self.openFolder()

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
        self.scrollArea.verticalScrollBar().valueChanged.connect(self.__on_scroll)
        main_layout.addWidget(self.scrollArea)

        # 設定中央小部件並添加佈局
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def __on_scroll(self):
        self.mode.on_scroll()

    def set_mode(self, mode: ViewerMode):
        if mode == ViewerMode.FOLDER_IMAGE:
            self.mode = FolderImageMode(self)
        elif mode == ViewerMode.MULTI_PAGE:
            self.mode = MultiImageMode(self)
            self.image_handler = ImageHandlerMulti()
        elif mode == ViewerMode.SINGLE_PAGE:
            self.mode = SingleImageMode(self)
            self.image_handler = ImageHandlerSingle()
        else:
            raise NotImplementedError("Mode", mode, "does not matched")

    def keyPressEvent(self, event: QKeyEvent):
        self.mode.key_press_event(event)

    def switch_mode(self, mode, folder_path):
        self.set_mode(mode)
        self.display_images(folder_path)

    def display_images(self, folder_path):
        self.image_handler.load_images([folder_path])
        self.image_handler.display_images(self.scrollArea)

    def display_files(self, folder_path):
        self.mode.display_files(folder_path)

    def openFolder(self, folder_path=None):
        """Open folder from file explorer"""

        # Check if the folder path is given
        if folder_path is None:
            folder_path = QFileDialog.getExistingDirectory(self, "打開資料夾", "")

        # Open files given the folder path
        if folder_path:
            self.toolbar.changeFolder(folder_path)
            self.display_files(folder_path)

    def folder_clicked(self, folder_path):
        self.toolbar.folder_clicked_log(folder_path)
        self.display_files(folder_path)

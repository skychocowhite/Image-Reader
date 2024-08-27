import os

from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget, QGridLayout, QDialog, QProgressBar, QApplication, QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QObject, QTimer

from .config_loader import ConfigLoader


class FolderImageReader(QObject):
    def __init__(self):
        super().__init__()
        self.callback = None
        config = ConfigLoader.load_config()
        self.image_height = config.get(
            "image_height", 400)                            # 設置顯示圖像的高度和寬度，從配置文件中加載
        self.image_width = config.get("image_width", 400)
        self.folder_path = None                             # 當前顯示的資料夾路徑
        # 用於顯示資料夾的滾動區域 (QScrollArea)
        self.scroll_area = None

        self.folders = []                                   # 儲存當前資料夾中的所有子資料夾路徑的列表
        self.folders_index = 0                              # 記錄當前加載的資料夾索引，用於分批加載資料夾
        self.folders_batch_size = 20                        # 每次批量加載資料夾的數量

        # Horizontal margin between items
        self.item_hmargin = 10
        self.active_module = None                           # 活動模組的標識符，可能用於處理不同的功能模組
        self.selected_index = 0                             # 記錄當前選擇的項目索引
        self.folder_widgets = []                            # 保存所有資料夾小部件的列表
        self.cols = 0                                       # 記錄顯示的列數，用於計算顯示布局
        self.is_loading = False                             # 標誌位，指示是否正在加載資料夾，以避免重複加載

    def set_callback(self, callback):  # 設置回調函數
        self.callback = callback

    def update_image_size(self, height, width):  # 更新圖片顯示大小
        self.image_height = height
        self.image_width = width
        self.adjust_layout()

    def adjust_layout(self):  # 重新調整佈局
        if self.folder_path:
            self.display_folders(self.folder_path, self.scroll_area)

    def display_folders(self, folder_path: str, scroll_area: QScrollArea):
        def _read_folders(folder_path):
            """讀取資料夾中的子資料夾"""
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    yield item_path

        self.folder_path = folder_path
        self.scroll_area = scroll_area
        # Read all subfolders
        self.folders = list(_read_folders(folder_path))

        # Initialize configuraiton of display
        self.cols = self.scroll_area.width() // (self.image_width + self.item_hmargin * 2)
        self.folders_index = 0
        self.folder_widgets = []
        self.selected_index = 0
        self._update_and_ensure_visible()

        # 創建內容佈局
        content_layout = QGridLayout()
        content_layout.setSpacing(self.item_hmargin)
        content_layout.setContentsMargins(
            self.item_hmargin, self.item_hmargin, self.item_hmargin, self.item_hmargin)

        # 設置滾動區域的內容
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)

        self.load_images()

        # 然後在初始化或適當的位置進行連接
        scroll_area.verticalScrollBar().valueChanged.connect(self._on_scroll_value_changed)

    def _on_scroll_value_changed(self):
        if not self.is_loading:
            self.is_loading = True

            # Check current position of scroll bar
            vertical_bar = self.scroll_area.verticalScrollBar()
            load_threshold = 300
            if self.active_module == 'folder_image_reader' and vertical_bar.value() + load_threshold >= vertical_bar.maximum():
                self.load_images()

            QTimer.singleShot(50, self._reset_loading_flag)  # 50毫秒後重置標誌位

    def _reset_loading_flag(self):
        self.is_loading = False

    def load_images(self, load_all=False):
        idx = self.folders_index
        num_folders = len(self.folders)
        if idx >= num_folders:  # 根據需要加載全部或更多圖像
            return

        # Get new index for more images
        # end_index is excluded
        end_index = num_folders if load_all else min(
            idx + self.folders_batch_size, num_folders)
        batch_size = end_index - idx

        # Display loading dialog
        progress_bar = QProgressBar()
        progress_bar.setMaximum(batch_size)
        layout = QVBoxLayout()
        layout.addWidget(progress_bar)

        loading_dialog = QDialog()
        loading_dialog.setWindowTitle('加載中...')
        loading_dialog.setModal(True)
        loading_dialog.setLayout(layout)
        loading_dialog.setGeometry(400, 300, 300, 100)
        loading_dialog.show()

        QApplication.processEvents()

        # Create widget for subfolder
        while idx < end_index:
            folder_widget = self._create_folder_widget(self.folders[idx])
            num_cols = self.scroll_area.width() // (self.image_width + 2 * self.item_hmargin)
            row = idx // num_cols
            col = idx % num_cols
            self.scroll_area.widget().layout().addWidget(folder_widget, row, col)
            self.folder_widgets.append(folder_widget)

            # 正確呼叫更新進度函數
            progress_bar.setValue(idx + 1)  # 更新進度條到當前索引
            if idx + 1 >= progress_bar.maximum():
                loading_dialog.accept()  # 當達到或超過最大值時關閉加載對話框
            idx += 1

        self.folders_index = idx
        loading_dialog.accept()  # 確保對話框在結束時關閉

    def _create_folder_widget(self, folder):
        """創建單個文件夾小部件"""

        def _create_label(folder, label_type='folder'):
            """根據類型創建並返回標籤"""
            label = QLabel(os.path.basename(folder)
                           if label_type == 'folder' else "")
            label.setAlignment(Qt.AlignCenter)
            label.mousePressEvent = lambda event, path=folder: self.callback(
                path)
            if label_type == 'folder':
                label.setWordWrap(True)
            return label

        folder_label = _create_label(folder, 'folder')
        image_label = _create_label(folder, 'image')

        folder_layout = QVBoxLayout()
        folder_layout.addWidget(image_label)
        folder_layout.addWidget(folder_label)
        folder_widget = QWidget()
        folder_widget.setLayout(folder_layout)

        # 獲取資料夾中的第一張圖片
        first_image_path = ""
        for filename in os.listdir(folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # 如果找到符合條件的文件，返回該文件的完整路徑
                first_image_path = os.path.join(folder, filename)
                break
        if first_image_path:
            pixmap = QPixmap(first_image_path).scaled(
                self.image_height, self.image_width, Qt.KeepAspectRatio)
            image_label.setPixmap(pixmap)

        return folder_widget

    def select_item(self, axis, direction):
        """根據給定的軸（列或行）和方向選擇下一個或上一個項目"""
        step = self.cols if axis == 'col' else 1  # 根據軸（列或行）設置步數
        new_index = self.selected_index + \
            (step if direction == 'next' else -step)  # 如果方向是 'next'，則增加步數，否則減少步數
        if 0 <= new_index < len(self.folder_widgets):  # 確保新的索引在有效範圍內
            self.selected_index = new_index
        self._update_and_ensure_visible()  # 更新佈局以確保所選項目可見並顯示選擇狀態

    def _update_and_ensure_visible(self):
        scroll_area = self.scroll_area
        scroll_bar = scroll_area.verticalScrollBar()

        for i, widget in enumerate(self.folder_widgets):
            if i == self.selected_index:
                widget.setStyleSheet("background-color: lightblue;")
                widget_top = widget.pos().y()
                widget_bottom = widget_top + widget.height()

                visible_area_top = scroll_bar.value()
                visible_area_bottom = visible_area_top + scroll_area.viewport().height()

                if widget_top < visible_area_top:
                    scroll_bar.setValue(widget_top)
                elif widget_bottom > visible_area_bottom:
                    scroll_bar.setValue(
                        widget_bottom - scroll_area.viewport().height())
            else:
                widget.setStyleSheet("")

    def select_current_item(self):
        if self.selected_index < len(self.folder_widgets):
            folder_widget = self.folder_widgets[self.selected_index]
            folder_label = folder_widget.layout().itemAt(1).widget()  # 獲取 folder_label
            folder_path = os.path.join(self.folder_path, folder_label.text())
            self.callback(folder_path)

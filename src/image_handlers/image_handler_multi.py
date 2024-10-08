from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt

from .image_handler import ImageHandler
from ..reader_mode import ViewerMode, ViewerStatus


class ImageHandlerMulti(ImageHandler):
    def __init__(self):
        super().__init__()

    def display_images(self, scroll_area: QScrollArea):
        self.content_layout = QVBoxLayout()
        self.content_widget = QWidget()
        self.content_widget.setLayout(self.content_layout)
        scroll_area.setWidget(self.content_widget)
        self.load_more_images()

    def __relocateImageIndex(self, scroll_area: QScrollArea):
        """Get index of the current viewing image"""

        # Get middle position of visible area
        current_ave_pos = scroll_area.verticalScrollBar().value() \
            + scroll_area.verticalScrollBar().pageStep() / 2

        for idx, label in enumerate(self.labels):
            start_pos = label.geometry().top()
            end_pos = label.geometry().bottom()
            if start_pos <= current_ave_pos and current_ave_pos <= end_pos:
                self.current_index = idx
                return

            # Check margin position betweeen images
            if idx < len(self.labels)-1:
                next_start_pos = self.labels[idx+1].geometry().top()
                if end_pos <= current_ave_pos and current_ave_pos <= next_start_pos:
                    self.current_index = idx
                    return

        # Default position in case
        self.current_index = len(self.labels)-1

    def on_scroll(self, scroll_area: QScrollArea):
        val2max = scroll_area.verticalScrollBar()
        threshold = 1000

        if len(self.labels) > 0:
            threshold = self.labels[0].height() * 5

        if ViewerStatus.current_mode == ViewerMode.MULTI_PAGE and val2max.value() + threshold >= val2max.maximum():
            self.__relocateImageIndex(scroll_area)
            self.load_more_images()

    def load_more_images(self, count=10):
        while len(self.labels) < len(self.images) and count > 0:
            img_path = self.images[len(self.labels)]
            pixmap = QPixmap(img_path)
            pixmap = pixmap.scaledToWidth(
                int(pixmap.width() * self.scale_factor), Qt.SmoothTransformation)

            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)

            self.content_layout.addWidget(label)
            self.labels.append(label)
            count -= 1

    def reload_images(self):
        num_preload_images = len(self.labels)
        for label in self.labels:
            self.content_layout.removeWidget(label)
            label.deleteLater()
        self.labels = []
        self.load_more_images(num_preload_images)

    def next_image(self, scroll_area: QScrollArea):
        self.__relocateImageIndex(scroll_area)
        if self.current_index == len(self.labels) - 1:
            self.load_more_images()

        self.__relocateImageIndex(scroll_area)
        if self.current_index < len(self.labels) - 1:
            self.current_index += 1
            label_position = self.labels[self.current_index].y()
            scroll_area.verticalScrollBar().setValue(label_position)

    def previous_image(self, scroll_area: QScrollArea):
        self.__relocateImageIndex(scroll_area)
        if self.current_index > 0:
            self.current_index -= 1
            label_position = self.labels[self.current_index].y()
            scroll_area.verticalScrollBar().setValue(label_position)

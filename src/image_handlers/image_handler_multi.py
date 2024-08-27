from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt

from .image_handler import ImageHandler


class ImageHandlerMulti(ImageHandler):
    def __init__(self):
        super().__init__()

    def display_images(self, scroll_area: QScrollArea):
        self.content_layout = QVBoxLayout()
        self.content_widget = QWidget()
        self.content_widget.setLayout(self.content_layout)
        scroll_area.setWidget(self.content_widget)
        scroll_area.verticalScrollBar().valueChanged.connect(
            lambda: self.on_scroll(scroll_area))
        self.load_more_images()

    def on_scroll(self, scroll_area: QScrollArea):
        val2max = scroll_area.verticalScrollBar()
        if self.active_module in ['multi'] and val2max.value() == val2max.maximum():
            self.load_more_images()

    def load_more_images(self):
        count = 10
        while self.current_index < len(self.images) and count > 0:
            img_path = self.images[self.current_index]
            pixmap = QPixmap(img_path)
            pixmap = pixmap.scaledToWidth(
                int(pixmap.width() * self.scale_factor), Qt.SmoothTransformation)

            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)

            self.content_layout.addWidget(label)
            self.labels.append(label)
            self.current_index += 1
            count -= 1

    def reload_images(self):
        for label in self.labels:
            self.content_layout.removeWidget(label)
            label.deleteLater()
        self.labels = []
        self.current_index = 0
        self.load_more_images()

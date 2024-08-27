from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt

from .image_handler import ImageHandler


class ImageHandlerSingle(ImageHandler):
    def __init__(self):
        super().__init__()

    def display_images(self, scroll_area: QScrollArea):
        self.content_layout = QVBoxLayout()
        self.content_widget = QWidget()
        self.content_widget.setLayout(self.content_layout)
        scroll_area.setWidget(self.content_widget)
        self.load_image()

    def on_scroll(self, scroll_area: QScrollArea):
        """No any operations needed"""
        pass

    def load_image(self):
        if self.current_index < len(self.images):
            img_path = self.images[self.current_index]
            pixmap = QPixmap(img_path)
            scaled_pixmap = pixmap.scaledToWidth(
                int(pixmap.width() * self.scale_factor), Qt.SmoothTransformation)

            label = QLabel()
            label.setPixmap(scaled_pixmap)
            label.setAlignment(Qt.AlignCenter)

            self.content_layout.addWidget(label)
            self.labels.append(label)

    def reload_images(self):
        for label in self.labels:
            self.content_layout.removeWidget(label)
            label.deleteLater()
        self.labels = []
        self.load_image()

    def next_image(self, scroll_area):
        scroll_area.verticalScrollBar().setValue(0)
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.reload_images()

    def previous_image(self, scroll_area):
        scroll_area.verticalScrollBar().setValue(0)
        if self.current_index > 0:
            self.current_index -= 1
            self.reload_images()

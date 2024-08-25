# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 12:56:21 2024

@author: hanks
"""

import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

from natsort import natsorted


class ImageHandler:
    def __init__(self):
        self.images = []
        self.current_index = 0
        self.labels = []
        self.scale_factor = 1.0
        self.active_module = None

    def load_images(self, folder_path):
        self.images = []
        self.current_index = 0
        self.labels = []
        for filename in natsorted(os.listdir(folder_path)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(folder_path, filename)
                self.images.append(img_path)

    def display_images(self, scroll_area):
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        scroll_area.setWidget(self.content_widget)
        scroll_area.verticalScrollBar().valueChanged.connect(
            lambda: self.on_scroll(scroll_area))
        self.load_more_images()

    def on_scroll(self, scroll_area):
        val2max = scroll_area.verticalScrollBar()
        if self.active_module in ['multi'] and val2max.value() == val2max.maximum():
            self.load_more_images()

    def load_more_images(self):
        count = 10
        while self.current_index < len(self.images) and count > 0:
            img_path = self.images[self.current_index]
            pixmap = QPixmap(img_path)
            scaled_pixmap = pixmap.scaledToWidth(
                int(pixmap.width() * self.scale_factor), Qt.SmoothTransformation)
            label = QLabel()
            label.setPixmap(scaled_pixmap)
            label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(label)
            self.labels.append(label)
            self.current_index += 1
            count -= 1

    def zoom(self, factor):
        self.scale_factor *= factor
        self.reload_images()

    def reload_images(self):
        for label in self.labels:
            self.content_layout.removeWidget(label)
            label.deleteLater()
        self.labels = []
        self.current_index = 0
        self.load_more_images()


class ImageHandlerSingle:
    def __init__(self):
        self.images = []
        self.current_index = 0
        self.labels = []
        self.scale_factor = 1.0
        self.active_module = None

    def load_images(self, folder_path):
        self.images = []
        self.current_index = 0
        self.labels = []
        for filename in natsorted(os.listdir(folder_path)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(folder_path, filename)
                self.images.append(img_path)

    def display_images(self, scroll_area):
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        scroll_area.setWidget(self.content_widget)
        self.load_image()

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

    def zoom(self, factor):
        self.scale_factor *= factor
        self.reload_images()

    def reload_images(self):
        for label in self.labels:
            self.content_layout.removeWidget(label)
            label.deleteLater()
        self.labels = []
        self.load_image()

    def next_image(self, scrollArea):
        scrollArea.verticalScrollBar().setValue(0)
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.reload_images()

    def previous_image(self, scrollArea):
        scrollArea.verticalScrollBar().setValue(0)
        if self.current_index > 0:
            self.current_index -= 1
            self.reload_images()

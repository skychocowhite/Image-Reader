# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 12:56:21 2024

@author: hanks, skychocowhite
"""

import os
from PyQt5.QtWidgets import QScrollArea, QLabel
from natsort import natsorted


class ImageHandler:
    def __init__(self):
        self.images: list[str] = []
        self.current_index = 0
        self.labels: list[QLabel] = []
        self.scale_factor = 1.0

    def load_images(self, folder_paths: list[str]):
        self.images = []
        self.current_index = 0
        self.labels = []

        for folder_path in folder_paths:
            for filename in natsorted(os.listdir(folder_path)):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(folder_path, filename)
                    self.images.append(img_path)

    def on_scroll(self, scroll_area: QScrollArea):
        return NotImplemented

    def display_images(self, scroll_area: QScrollArea):
        return NotImplemented

    def reload_images(self):
        return NotImplemented

    def next_image(self, scroll_area: QScrollArea):
        return NotImplemented

    def previous_image(self, scroll_area: QScrollArea):
        return NotImplemented

    def zoom(self, factor):
        self.scale_factor *= factor
        self.reload_images()

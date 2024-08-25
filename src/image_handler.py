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
        self.selected_folders = []      # 儲存選取的資料夾路徑
        self.current_folder_index = 0   # 當前處於選取資料夾的索引
        self.content_layout = None      # 用於存儲顯示圖片的佈局
        self.content_widget = None      # 用於存儲顯示圖片的主體
        self.folder_order = []          # 用於記錄資料夾的讀取順序

    def load_images_from_folders(self, folders, scroll_area):
        """從多個已選取的資料夾中加載圖片並存儲圖片路徑"""
        self.images = []  # 清空之前的圖片路徑
        self.selected_folders = folders  # 更新選取的資料夾
        self.folder_order = list(range(len(folders)))  # 初始化資料夾順序
        self.current_folder_index = 0    # 重置資料夾索引
        self.current_index = 0           # 重置圖片索引
        self.labels = []                 # 清空之前的圖片顯示

    def load_next_folder_images(self):
        """加載下一個資料夾中的圖片"""
        while self.current_folder_index < len(self.folder_order):
            folder_index = self.folder_order[self.current_folder_index]
            folder_path = self.selected_folders[folder_index]
            # print(f"Loading images from folder: {folder_path}")
            self._load_images_from_folder(folder_path)
            self.current_folder_index += 1
            if len(self.images) > 0:  # 當加載到圖片時立即停止循環以進行顯示
                # print(f"Images loaded: {len(self.images)}")
                break
        self.load_more_images()  # 加載完圖片後顯示圖片

    def _load_images_from_folder(self, folder_path):
        """從指定資料夾中獲取所有圖片的路徑"""
        images = []
        for filename in natsorted(os.listdir(folder_path)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(folder_path, filename)
                images.append(image_path)
        self.images.extend(images)  # 將加載的圖片添加到總圖片列表中
        # print(f"Images from {folder_path}: {images}")

    def display_images(self, scroll_area):
        """初始化佈局並顯示圖片"""
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        scroll_area.setWidget(self.content_widget)
        scroll_area.verticalScrollBar().valueChanged.connect(lambda: self.on_scroll(scroll_area))
        self.load_more_images()

    def on_scroll(self, scroll_area):
        val2max = scroll_area.verticalScrollBar()
        if self.active_module in ['multi'] and val2max.value() == val2max.maximum():
            self.load_more_images()

    def load_more_images(self):
        """滾動加載更多圖片"""
        count = 10
        while self.current_index < len(self.images) and count > 0:
            img_path = self.images[self.current_index]
            # print(f"Displaying image: {img_path}")
            pixmap = QPixmap(img_path)
            scaled_pixmap = pixmap.scaledToWidth(int(pixmap.width() * self.scale_factor), Qt.SmoothTransformation)
            label = QLabel()
            label.setPixmap(scaled_pixmap)
            label.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(label)
            self.labels.append(label)
            self.current_index += 1
            count -= 1
        
        # 如果當前資料夾中的圖片已加載完畢，且還有未加載的資料夾，則繼續加載下一個資料夾的圖片
        if self.current_index >= len(self.images) and self.current_folder_index < len(self.folder_order):
            self.load_next_folder_images()

    def zoom(self, factor):
        self.scale_factor *= factor
        self.reload_images()

    def reload_images(self):
        """重新加載圖片，主要用於縮放操作後"""
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
            scaled_pixmap = pixmap.scaledToWidth(int(pixmap.width() * self.scale_factor), Qt.SmoothTransformation)
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

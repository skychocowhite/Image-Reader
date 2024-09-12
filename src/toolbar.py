import pathlib
from enum import Enum

from PyQt5.QtWidgets import (QToolBar, QAction, QLabel, QDialog,
                             QVBoxLayout, QSlider, QDialogButtonBox, QLineEdit)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


from .reader_mode import ViewerMode
from .config.config_loader import ConfigLoader


class MainToolBar(QToolBar):
    def __init__(self, parent):
        super().__init__("主工具欄", parent)
        self.setParent(parent)
        self.folder_stack = []
        self.config = ConfigLoader.load_config()
        self.image_height = self.config.get("image_height", 400)
        self.image_width = self.config.get("image_width", 400)
        self.asset_path = str(pathlib.Path(
            __file__).parent.absolute()) + '/_assets_/'
        self.actions: dict[str, QAction] = {}
        self.initUI()

    def initUI(self):
        open_action = QAction(
            QIcon(self.asset_path + 'open.png'), '打開文件夾', self)
        open_action.triggered.connect(lambda: self.parent().openFolder())
        self.actions[self.ToolbarActions.OPEN_FOLDER] = open_action
        self.addAction(open_action)

        back_action = QAction(
            QIcon(self.asset_path + 'back.png'), '返回上一頁', self)
        back_action.triggered.connect(self.go_back)
        back_action.setEnabled(False)
        self.actions[self.ToolbarActions.BACK] = back_action
        self.addAction(back_action)

        adjust_scroll_action = QAction(
            QIcon(self.asset_path + 'adjust.png'), '調整滾動行數', self)
        adjust_scroll_action.triggered.connect(self.open_adjust_scroll_dialog)
        self.actions[self.ToolbarActions.ADJUST_SCROLL] = adjust_scroll_action
        self.addAction(adjust_scroll_action)

        adjust_layout_action = QAction(
            QIcon(self.asset_path + 'relayout.png'), '重新調整佈局', self)
        adjust_layout_action.triggered.connect(
            self.parent().image_reader.adjust_layout)
        self.actions[self.ToolbarActions.ADJUST_LAYOUT] = adjust_layout_action
        self.addAction(adjust_layout_action)

        settings_action = QAction(
            QIcon(self.asset_path + 'setting.png'), '設定', self)
        settings_action.triggered.connect(self.open_settings_dialog)
        self.actions[self.ToolbarActions.SETTINGS] = settings_action
        self.addAction(settings_action)

        single_page_action = QAction(
            QIcon(self.asset_path + 'single_page.png'), '單頁模式', self)
        single_page_action.triggered.connect(
            lambda: self.parent().switch_mode(ViewerMode.SINGLE_PAGE, self.folder_stack[-1]))
        self.actions[self.ToolbarActions.SINGLE_PAGE] = single_page_action
        self.addAction(single_page_action)

        multi_page_action = QAction(
            QIcon(self.asset_path + 'multi_page.png'), '多頁模式', self)
        multi_page_action.triggered.connect(
            lambda: self.parent().switch_mode(ViewerMode.MULTI_PAGE, self.folder_stack[-1]))
        self.actions[self.ToolbarActions.MULTI_PAGE] = multi_page_action
        self.addAction(multi_page_action)

        multi_choice_action = QAction(
            QIcon(self.asset_path + 'choice.png'), '選擇多項', self)
        # multi_choice_action.triggered.connect(...) # TODO: add multiple triggered method
        self.actions[self.ToolbarActions.MULTI_CHOICE] = multi_choice_action
        self.addAction(multi_choice_action)

        self.path_label = QLabel()
        self.addWidget(self.path_label)

    def changeMultiChoiceState(self, state):
        self.actions[self.ToolbarActions.MULTI_CHOICE].setEnabled(state)

    def changeFolder(self, folder_path):
        self.folder_stack.append(folder_path)
        self.path_label.setText(folder_path)
        if len(self.folder_stack) > 1:
            self.actions[self.ToolbarActions.BACK].setEnabled(True)

    def go_back(self):
        if len(self.folder_stack) > 1:
            self.folder_stack.pop()
            previous_folder = self.folder_stack[-1]
            self.path_label.setText(previous_folder)
            self.parent().displayFiles(previous_folder)
        if len(self.folder_stack) <= 1:
            self.actions[self.ToolbarActions.BACK].setEnabled(False)

    def folder_clicked_log(self, folder_path):
        self.folder_stack.append(folder_path)
        self.path_label.setText(folder_path)
        self.actions[self.ToolbarActions.BACK].setEnabled(True)

    def open_adjust_scroll_dialog(self):
        dialog = self.AdjustScrollDialog(self)
        if dialog.exec() == QDialog.Accepted:
            value = dialog.get_value()
            self.parent().scrollArea.verticalScrollBar().setSingleStep(value)

    def open_settings_dialog(self):
        dialog = self.SettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            size = dialog.get_image_size()
            self.update_image_size(size['height'], size['width'])
            self.config['image_height'] = size['height']
            self.config['image_width'] = size['width']
            ConfigLoader.save_config(self.config)

    def update_image_size(self, height, width):
        self.parent().image_reader.update_image_size(height, width)

    class ToolbarActions(Enum):
        OPEN_FOLDER = 'open_folder'
        BACK = 'back'
        ADJUST_SCROLL = 'adjust_scroll'
        ADJUST_LAYOUT = 'adjust_layout'
        SETTINGS = 'settings'
        SINGLE_PAGE = 'single_page'
        MULTI_PAGE = 'multi_page'
        MULTI_CHOICE = 'multi_choice'

    class AdjustScrollDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.setWindowTitle("調整滾動行數")
            self.setGeometry(200, 200, 300, 100)

            layout = QVBoxLayout()

            self.slider = QSlider(Qt.Horizontal)
            self.slider.setMinimum(300)
            self.slider.setMaximum(1000)
            self.slider.setValue(800)
            self.slider.setTickPosition(QSlider.TicksBelow)
            self.slider.setTickInterval(100)
            layout.addWidget(self.slider)

            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            layout.addWidget(buttons)

            self.setLayout(layout)

        def get_value(self):
            return self.slider.value()

    class SettingsDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.setWindowTitle('Settings')
            self.setGeometry(200, 200, 400, 200)

            layout = QVBoxLayout()

            self.image_height_label = QLabel('Image Height:')
            self.image_height_input = QLineEdit(self)
            self.image_height_input.setText(str(parent.image_height))
            layout.addWidget(self.image_height_label)
            layout.addWidget(self.image_height_input)

            self.image_width_label = QLabel('Image Width:')
            self.image_width_input = QLineEdit(self)
            self.image_width_input.setText(str(parent.image_width))
            layout.addWidget(self.image_width_label)
            layout.addWidget(self.image_width_input)

            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            layout.addWidget(buttons)

            self.setLayout(layout)

        def get_image_size(self):
            return {
                'height': int(self.image_height_input.text()),
                'width': int(self.image_width_input.text())
            }

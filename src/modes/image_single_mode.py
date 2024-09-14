from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QScrollBar

from ..toolbar import ToolbarActions
from .reader_mode import ViewerMode
from .mode import Mode

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..image_viewer import ImageViewer


class SingleImageMode(Mode):
    def __init__(self, image_viewer: 'ImageViewer'):
        super().__init__(image_viewer)

        self.scroll_map = {
            Qt.Key_W: QScrollBar.SliderSingleStepSub,
            Qt.Key_Space: QScrollBar.SliderSingleStepAdd,
            Qt.Key_S: QScrollBar.SliderSingleStepAdd,
        }

        self.__set_toolbar_action()

    def __set_toolbar_action(self):
        self.image_viewer.toolbar.actions[ToolbarActions.MULTI_CHOICE].setEnabled(
            False)
        self.image_viewer.toolbar.actions[ToolbarActions.MULTI_PAGE].setEnabled(
            True)
        self.image_viewer.toolbar.actions[ToolbarActions.SINGLE_PAGE].setEnabled(
            True)

    def key_press_event(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        # 检查 Ctrl 修饰键，并应用于 multi 和 single 模式
        if modifiers == Qt.ControlModifier:
            if key == Qt.Key_W:
                self.image_viewer.image_handler.zoom(1.25)  # 放大
            elif key == Qt.Key_S:
                self.image_viewer.image_handler.zoom(0.8)   # 縮小
        elif key in self.scroll_map:
            self.image_viewer.scrollArea.verticalScrollBar(
            ).triggerAction(self.scroll_map[key])
        elif key == Qt.Key_Escape:
            self.image_viewer.toolbar.go_back()
        elif key == Qt.Key_D:
            self.image_viewer.image_handler.next_image(
                self.image_viewer.scrollArea)
        elif key == Qt.Key_A:
            self.image_viewer.image_handler.previous_image(
                self.image_viewer.scrollArea)

    def get_mode(self) -> ViewerMode:
        return ViewerMode.SINGLE_PAGE

    def on_scroll(self):
        # No need for scroll event
        pass

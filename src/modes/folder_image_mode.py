from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

from ..reader_mode import ViewerMode
from .mode import Mode

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..image_viewer import ImageViewer


class FolderImageMode(Mode):
    def __init__(self, image_viewer: "ImageViewer"):
        super().__init__(image_viewer)

        # Direction key not working
        self.navigation_map = {
            Qt.Key_F5: lambda: self.image_viewer.image_reader.adjust_layout(),
            Qt.Key_W: lambda: self.image_viewer.image_reader.select_item('col', 'previous'),
            Qt.Key_Up: lambda: self.image_viewer.image_reader.select_item('col', 'previous'),
            Qt.Key_S: lambda: self.image_viewer.image_reader.select_item('col', 'next'),
            Qt.Key_Down: lambda: self.image_viewer.image_reader.select_item('col', 'next'),
            Qt.Key_A: lambda: self.image_viewer.image_reader.select_item('row', 'previous'),
            Qt.Key_Left: lambda: self.image_viewer.image_reader.select_item('row', 'previous'),
            Qt.Key_D: lambda: self.image_viewer.image_reader.select_item('row', 'next'),
            Qt.Key_Right: lambda: self.image_viewer.image_reader.select_item('row', 'next'),
            Qt.Key_Return: lambda: self.image_viewer.image_reader.select_current_item(),
            Qt.Key_O: lambda: self.image_viewer.openFolder(),
            Qt.Key_F: lambda: self.image_viewer.image_reader.load_images(
                load_all=True)
        }

    def key_press_event(self, event: QKeyEvent):
        key = event.key()

        if key in self.navigation_map:
            self.navigation_map[key]()

    def get_mode(self) -> ViewerMode:
        return ViewerMode.FOLDER_IMAGE

    def on_scroll(self):
        self.image_viewer.image_reader.on_scroll_value_changed()

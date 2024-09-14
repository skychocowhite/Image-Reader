import os

from PyQt5.QtGui import QKeyEvent

from ..reader_mode import ViewerMode

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..image_viewer import ImageViewer


class Mode:
    def __init__(self, image_viewer: "ImageViewer"):
        self.image_viewer = image_viewer

    def key_press_event(self, event: QKeyEvent):
        raise NotImplementedError("Base class \"Mode\" does not support")

    def display_files(self, folder_path: str):
        filenames: list[str] = list(
            filename for filename in os.listdir(folder_path))

        # Reset scroll bar
        self.image_viewer.scrollArea.verticalScrollBar().setValue(0)

        # Check if all files in folder are images
        all_images = all(filename.lower().endswith(('.png', '.jpg', '.jpeg'))
                         for filename in filenames)

        if all_images:
            self.image_viewer.set_mode(ViewerMode.MULTI_PAGE)
            self.image_viewer.display_images(folder_path)
        else:
            self.image_viewer.set_mode(ViewerMode.FOLDER_IMAGE)
            self.image_viewer.image_reader.displayFiles(
                folder_path, self.image_viewer.scrollArea)

    def get_mode(self) -> ViewerMode:
        raise NotImplementedError("Base class \"Mode\" does not support")

    def on_scroll(self):
        raise NotImplementedError("Base class \"Mode\" does not support")

from enum import Enum


class ViewerMode(Enum):
    FOLDER_IMAGE = 'folder_image'
    MULTI_PAGE = 'multi_page'
    SINGLE_PAGE = 'single_page'


class ViewerStatus():
    current_mode = ''

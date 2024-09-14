import sys
from PyQt5.QtWidgets import QApplication
from src.image_viewer import ImageViewer


def main():
    app = QApplication(sys.argv)  # 初始化 QApplication
    viewer = ImageViewer()        # 建立 ImageViewer 物件
    viewer.show()                 # 顯示 ImageViewer 視窗
    sys.exit(app.exec())          # 進入應用程式事件迴圈


if __name__ == '__main__':
    main()

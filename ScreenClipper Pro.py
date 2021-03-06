from io import BytesIO

import keyboard
import numpy as np
import PyQt5
import win32clipboard
from PIL import Image
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *


class Window(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setGeometry(0, 0, WIDTH, HEIGHT)
        self.setWindowOpacity(0.001)
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap('icon.png')))
        self.setWindowTitle('ScreenClipper Pro')
        
        self.start = False
        self.im = [0, 0, 0, 0]

        self.sc = App.primaryScreen()

        self.image = self.sc.grabWindow(0)

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(0, 0, WIDTH, HEIGHT)
        self.label.setPixmap(self.image)
        self.setCursor(Qt.CrossCursor)

        self.front = QtWidgets.QWidget(self)
        self.front.setStyleSheet('background-color: rgba(0, 0, 0, 100)')
        self.front.setGeometry(0, 0, WIDTH, HEIGHT)
        

        self.old_x = 0
        self.old_y = 0
        
        self.rectangable = QtWidgets.QLabel(self)
        self.rectangable.setStyleSheet('border: 2px solid red')
        self.rectangable.hide()

        self.byte_array = QByteArray()
        self.buffer = QBuffer(self.byte_array)
        self.buffer.open(self.buffer.ReadWrite)

        
        self.show()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_rect = [event.x(), event.y()]
            self.start = True
        return super().mousePressEvent(event)



    def mouseMoveEvent(self, event):
        if self.start:
            self.update()
            self.rectangable.setGeometry(
                self.old_rect[0],
                self.old_rect[1],
                event.x() - self.old_rect[0],
                event.y() - self.old_rect[1]
            )
            im = self.image.copy(
                self.old_rect[0] + 2,
                self.old_rect[1],
                event.x() - self.old_rect[0],
                event.y() - self.old_rect[1]
            )
            self.rectangable.setPixmap(im)
            self.rectangable.show()
        return super().mouseMoveEvent(event)



    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
        
            self.start    = False
            self.new_rect = [event.x(), event.y()]
            
            self.im = [
                self.old_rect[0],
                self.old_rect[1],
                self.new_rect[0] - self.old_rect[0],
                self.new_rect[1] - self.old_rect[1]
            ]

            if self.im[2] >= 10 and self.im[3] >= 10:
                
                self.rectangable.setGeometry(
                    self.im[0],
                    self.im[1],
                    self.im[2],
                    self.im[3]
                )
                self.rectangable.show()
                self.image = self.image.copy(
                    self.im[0],
                    self.im[1],
                    self.im[2],
                    self.im[3]
                )

                self.image = self.image.toImage().convertToFormat(QtGui.QImage.Format.Format_RGBA8888)

                width  = self.image.width()
                height = self.image.height()

                image_bits = self.image.bits()
                image_bits.setsize(width * height * 4)
                arr = np.array(image_bits).reshape((height, width, 4))


                image = Image.fromarray(arr)

                output = BytesIO()
                image.convert("RGB").save(output, "BMP")
                data = output.getvalue()[14:]
                output.close()

                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()

                del self.image
                del image_bits
                del image
                del data
                
                self.hide()
            else:
                self.rectangable.hide()

        return super().mouseReleaseEvent(event)


    def show(self):
        self.anim = QVariantAnimation()
        self.anim.setStartValue(0.001)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(200)
        self.anim.valueChanged.connect(self.setWindowOpacity)
        self.anim.start()
        super().show()


    def hide(self):
        self.anim = QVariantAnimation()
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setDuration(200)
        self.anim.valueChanged.connect(self.setWindowOpacity)
        self.anim.start()


    def setWindowOpacity(self, level):
        if level == 0:
            self.close()
            App.quit()
        return super().setWindowOpacity(level)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        return super().keyPressEvent(event)






if __name__ == "__main__":
    import sys
    import time
    
    App = QtWidgets.QApplication([])

    desktop = QtWidgets.QDesktopWidget()
    WIDTH   = desktop.width()
    HEIGHT  = desktop.height()

    while True:
        if keyboard.is_pressed('prnt scrn'):
            window = Window()
            # window.close()
            App.exec_()

        time.sleep(0.1)

    sys.exit()

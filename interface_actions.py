from dicom import Ui_DICOM
from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
from PyQt5.QtWidgets import QMessageBox,QDialog,QPushButton,QLineEdit





class Interface_actions(QtWidgets.QMainWindow,Ui_DICOM):
        def __init__(self):
                super(Interface_actions,self).__init__()
                self.setupUi(self)
                self.dragPos = QtCore.QPoint()
                
        def mousePressEvent(self, event):
                self.dragPos = event.globalPos()

        def mouseMoveEvent(self, event):
                if event.buttons() == QtCore.Qt.LeftButton:
                        self.move(self.pos() + event.globalPos() - self.dragPos)
                        self.dragPos = event.globalPos()
                        event.accept()  

        def menu_slide(self):
            width=self.nav_drw.width()
            if width == 0:
                    newWidth=200
            else:
                    newWidth=0
            self.animation=QtCore.QPropertyAnimation(self.nav_drw,b"minimumWidth")
            self.animation.setDuration(300)
            self.animation.setStartValue(width)
            self.animation.setEndValue(newWidth)
            self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation.start()

        def change_page(self,page_no):
                self.running = False
                self.main_pages_vwr.setCurrentIndex(page_no)
                width=self.nav_drw.width()
                if width == 200:
                        newWidth=0
                else:
                        newWidth=0
                self.animation=QtCore.QPropertyAnimation(self.nav_drw,b"minimumWidth")
                self.animation.setDuration(300)
                self.animation.setStartValue(width)
                self.animation.setEndValue(newWidth)
                self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
                self.animation.start()

        def Close(self):
                self.running = False
                self.close()

        def minimize(self):
                self.running = False
                self.showMinimized()

        def show_filters(self):
                height=self.filters_drw.height()
                height1=self.filters_sliders.height()
                if height == 0:
                        new=370
                        self.animation=QtCore.QPropertyAnimation(self.filters_drw,b"maximumHeight")
                        self.animation.setDuration(300)
                        self.animation.setStartValue(height)
                        self.animation.setEndValue(new)
                        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
                        self.animation.start()

                        new=375
                        self.animation2=QtCore.QPropertyAnimation(self.filters_sliders,b"maximumHeight")
                        self.animation2.setDuration(300)
                        self.animation2.setStartValue(height1)
                        self.animation2.setEndValue(new)
                        self.animation2.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
                        self.animation2.start()
                        self.brightness_lbl.show()
                        self.blur_lbl.show()
                
                else:
                        new=0
                        self.animation=QtCore.QPropertyAnimation(self.filters_drw,b"maximumHeight")
                        self.animation.setDuration(300)
                        self.animation.setStartValue(height)
                        self.animation.setEndValue(new)
                        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
                        self.animation.start()
                        
                        self.animation2=QtCore.QPropertyAnimation(self.filters_sliders,b"maximumHeight")
                        self.animation2.setDuration(300)
                        self.animation2.setStartValue(height1)
                        self.animation2.setEndValue(new)
                        self.animation2.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
                        self.animation2.start()
                        self.brightness_lbl.hide()
                        self.blur_lbl.hide()

        
      
                
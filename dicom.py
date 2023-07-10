from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtWidgets import QMessageBox, QWidget, QLabel, QVBoxLayout,QFileDialog
from PyQt5.QtCore import Qt
import numpy as np
import os
import random
import pydicom
import qimage2ndarray as imgia
import time


glob_cine_counter=0
p_space=0
folder_path=None
planes_list=[]
dicom_info=[]



file_path=None
filtered=None
brightness_value_now = 0  
blur_value_now = 0

class image_lbl(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(150)
        self.setMinimumWidth(150)
        self.setAcceptDrops(True)
        self.setText('\n\n Drop Image Here \n\n')
        self.setFont(QFont('Arial',15))
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #fff;
                color: rgb(255, 255, 255);
            }
        ''')

    def setPixmap(self, image):
        super().setPixmap(image)


class Image_Drag_Drop(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 300)
        self.setMinimumWidth(300)
        self.setMaximumHeight(300)
        self.setAcceptDrops(True)
        mainLayout = QVBoxLayout()
        self.photoViewer = image_lbl()
        mainLayout.addWidget(self.photoViewer)
        mainLayout.setAlignment(Qt.AlignCenter)
        self.setLayout(mainLayout)
        

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            global file_path
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.set_image(file_path)
            event.accept()
            
        else:
            event.ignore()

    def ret_file():
        return file_path

    def set_image(self, file_path):
        self.photoViewer.setPixmap(QPixmap(file_path).scaled(300,300,Qt.KeepAspectRatio))

    def edge_image(self, file_path):
        if file_path is None:
            return
        im=cv2.imread(file_path)
        # lap=im.copy()
        # k= np.array([[ -1,  -1,  -1],
        #              [ -1,   8,  -1],
        #              [ -1,  -1,  -1]
        #              ])
        # for q in range(3):
        #     for i in range((k.shape[0]//2),im.shape[0]-(k.shape[0]//2)):
        #         for j in range((k.shape[1]//2),im.shape[1]-(k.shape[1]//2)):
        #             m=0
        #             for o in range(-(k.shape[0]//2),(k.shape[0]//2)+1):
        #                 for u in range(-(k.shape[1]//2),(k.shape[1]//2)+1):
        #                     m+=im[i+o][j+u][q]*k[o][u]
        #             lap[i][j][q]=m
        im=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        lap= cv2.Canny(im,100,200)
        ll=cv2.cvtColor(lap,cv2.COLOR_BGR2RGB)
        global filtered
        filtered=lap.copy()
        image=QImage(ll,ll.shape[1],ll.shape[0],ll.strides[0],QImage.Format_RGB888)
        self.photoViewer.setPixmap(QPixmap.fromImage(image).scaled(300,300,Qt.KeepAspectRatio))

    def threshold(self,file_path):
        if file_path is None:
            return
        img = cv2.imread(file_path)

        # convert image from rgb to grayscale
        # r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]
        # gray =  0.299 * r + 0.587 * g + 0.114 *b

        img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        bw=img.copy()
        dialog= QtWidgets.QInputDialog(self)
        dialog.setStyleSheet('''
                             *{ color: white; font-weight: bold;}

                             QLabel{ color: rgb(255, 255, 255);font-weight: bold; font-size:12px;}

                             QPushButton{ 
                             height:20px;
                             width:50px;
                             background-color: rgb(47, 11, 255);
                             color: rgb(255, 255, 255);
                             font-weight: bold; border-style:outset;
                             border-radius:10px;
                             }
                            
                             QPushButton::pressed{background-color: rgb(152, 223, 255);
                             color:black;
                             border-style:inset;}
                             
                                  
                             ''')
        vl,chk=dialog.getInt(dialog,"Threshold","Enter The Threshold Value",value=150,min=0,max=255)
        # if dialog.exec_() == QDialog.Accepted:
        #     text = dialog.textValue()
        #     self.le.setText(text)
        # thresholding function
        if chk:
            bw= cv2.threshold(img,vl,255,cv2.THRESH_BINARY)[1]
        
        ll=bw.copy()
        global filtered
        filtered=ll.copy()
        image=QImage(ll,ll.shape[1],ll.shape[0],ll.strides[0],QImage.Format_Grayscale8)
        self.photoViewer.setPixmap(QPixmap.fromImage(image).scaled(300,300,Qt.KeepAspectRatio))

    def blur_image(self,file_path,val):
            if file_path is None:
                return
            im=cv2.imread(file_path)
            bl=im.copy()
            # k= np.array([[ 1,  1,  1],
            #              [ 1,  1,  1],
            #              [ 1,  1,  1]
            #              ])
            # for q in range(3):
            #     for i in range((k.shape[0]//2),im.shape[0]-(k.shape[0]//2)):
            #         for j in range((k.shape[1]//2),im.shape[1]-(k.shape[1]//2)):
            #             m=0
            #             for o in range(-(k.shape[0]//2),(k.shape[0]//2)+1):
            #                 for u in range(-(k.shape[1]//2),(k.shape[1]//2)+1):
            #                     m+=im[i+o][j+u][q]*k[o][u]/9
            #             bl[i][j][q]=m
            kernel_size = (val + 1, val + 1)  
            bl= cv2.blur(bl, kernel_size)
            ll=cv2.cvtColor(bl,cv2.COLOR_BGR2RGB)
            global filtered
            filtered=bl.copy()
            image=QImage(ll,ll.shape[1],ll.shape[0],ll.strides[0],QImage.Format_RGB888)
            self.photoViewer.setPixmap(QPixmap.fromImage(image).scaled(300,300,Qt.KeepAspectRatio))


    def bright_image(self,file_path, value):
        if file_path is None:
            return
        im=cv2.imread(file_path)
        br=im.copy()
        hsv = cv2.cvtColor(br, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        lim = 255 - value
        v[v > lim] = 255
        v[v <= lim] += value
        final_hsv = cv2.merge((h, s, v))
        img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        ll=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        global filtered
        filtered=img.copy()
        image=QImage(ll,ll.shape[1],ll.shape[0],ll.strides[0],QImage.Format_RGB888)
        self.photoViewer.setPixmap(QPixmap.fromImage(image).scaled(300,300,Qt.KeepAspectRatio))
        

    def blur_value(self, value):
        global blur_value_now
        blur_value_now = value
        #print('Blur: ', value)
        self.update()

    
    def brightness_value(self, value):
        global brightness_value_now
        brightness_value_now = value
        #print('Brightness: ', value)
        self.update2()

    def update(self):
        self.blur_image(file_path,blur_value_now)

    def update2(self): 
        self.bright_image(file_path,brightness_value_now)

    def save_image(self,filtered):
            if filtered is None:
                    return
            else:
                    path=os.getcwd().replace("\\","\\\\")
                    cv2.imwrite(path+"\\filtered_images\\filtered_image_"+str(random.randint(0,9999))+".png",filtered)
                    

    def clear_image(self):
            self.photoViewer.clear()
            self.photoViewer.setText('\n\n Drop Image Here \n\n')
            self.photoViewer.setFont(QFont('Arial',15))
            self.photoViewer.setStyleSheet('''
            QLabel{
                border: 4px dashed #fff;
                color: rgb(255, 255, 255);
            } ''')
            global filtered
            filtered=None
            global file_path
            file_path=None

    def invert(self,file_path):
        if file_path is None:
            return
        img = cv2.imread(file_path)
        com=255-img
        global filtered
        filtered=com.copy()
        ll=cv2.cvtColor(com,cv2.COLOR_BGR2RGB)
        # cv2.imwrite("C:\\Users\\HTG\\Desktop\\jeje.png",filtered)
        image=QImage(ll,ll.shape[1],ll.shape[0],ll.strides[0],QImage.Format_RGB888)
        self.photoViewer.setPixmap(QPixmap.fromImage(image).scaled(300,300,Qt.KeepAspectRatio))

    def set_dicom_img(self,path):
        dc=pydicom.dcmread(path)
        dc_img=dc.pixel_array
        img=(dc_img/dc_img.max()*255)
        ll=cv2.cvtColor(np.uint8(img),cv2.COLOR_GRAY2RGB)
        dcm_img=ll.copy()
        path=os.getcwd().replace("\\","\\\\")
        cv2.imwrite(path+"\\dcm\\dcm_img.png",dcm_img)
        image=QImage(ll,ll.shape[1],ll.shape[0],ll.strides[0],QImage.Format_RGB888)
        global file_path
        file_path=path+"\\dcm\\dcm_img.png"
        self.photoViewer.setPixmap(QPixmap.fromImage(image).scaled(300,300,Qt.KeepAspectRatio))

    

class Ui_DICOM(object):
    def setupUi(self, DICOM):
        DICOM.setObjectName("DICOM")
        DICOM.resize(1000, 600)
        DICOM.setMinimumSize(QtCore.QSize(1000, 600))
        DICOM.setMaximumSize(QtCore.QSize(1000, 600))
        DICOM.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.main = QtWidgets.QWidget(DICOM)
        self.main.setStyleSheet("background-color: rgb(45, 45, 45);")
        self.main.setObjectName("main")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.main)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.top_bar = QtWidgets.QFrame(self.main)
        self.top_bar.setMaximumSize(QtCore.QSize(16777215, 40))
        self.top_bar.setStyleSheet("background-color: rgb(4, 4, 4);")
        self.top_bar.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.top_bar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.top_bar.setObjectName("top_bar")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.top_bar)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tog_frm = QtWidgets.QFrame(self.top_bar)
        self.tog_frm.setMinimumSize(QtCore.QSize(70, 0))
        self.tog_frm.setMaximumSize(QtCore.QSize(90, 16777215))
        self.tog_frm.setStyleSheet("QPushButton::hover{\n"
"\n"
"    background-color: rgb(145, 143, 143);\n"
"\n"
"}")
        self.tog_frm.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tog_frm.setFrameShadow(QtWidgets.QFrame.Raised)
        self.tog_frm.setObjectName("tog_frm")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tog_frm)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tgl_btn = QtWidgets.QPushButton(self.tog_frm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tgl_btn.sizePolicy().hasHeightForWidth())
        self.tgl_btn.setSizePolicy(sizePolicy)
        self.tgl_btn.setMinimumSize(QtCore.QSize(0, 30))
        self.tgl_btn.setMaximumSize(QtCore.QSize(90, 90))
        self.tgl_btn.setStyleSheet("QPushButton{\n"
"color: rgb(255, 255, 255);\n"
"\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"background-color: rgb(224, 255, 238);\n"
"    border-style:inset;\n"
"\n"
"}")
        self.tgl_btn.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ii/images/men.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.tgl_btn.setIcon(icon)
        self.tgl_btn.setIconSize(QtCore.QSize(24, 24))
        self.tgl_btn.setFlat(True)
        self.tgl_btn.setObjectName("tgl_btn")
        self.verticalLayout_2.addWidget(self.tgl_btn)
        self.horizontalLayout.addWidget(self.tog_frm)
        self.frame_top = QtWidgets.QFrame(self.top_bar)
        self.frame_top.setMinimumSize(QtCore.QSize(810, 0))
        self.frame_top.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_top.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_top.setObjectName("frame_top")
        self.horizontalLayout.addWidget(self.frame_top)
        self.cntrl_frm = QtWidgets.QFrame(self.top_bar)
        self.cntrl_frm.setMinimumSize(QtCore.QSize(110, 40))
        self.cntrl_frm.setMaximumSize(QtCore.QSize(90, 50))
        self.cntrl_frm.setStyleSheet("")
        self.cntrl_frm.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.cntrl_frm.setFrameShadow(QtWidgets.QFrame.Raised)
        self.cntrl_frm.setObjectName("cntrl_frm")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.cntrl_frm)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.minimize_btn = QtWidgets.QPushButton(self.cntrl_frm)
        self.minimize_btn.setMinimumSize(QtCore.QSize(0, 26))
        self.minimize_btn.setStyleSheet("QPushButton{\n"
"color: rgb(255, 255, 255);\n"
"\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"background-color: rgb(224, 255, 238);\n"
"    border-style:inset;\n"
"\n"
"}")
        self.minimize_btn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/ii/images/minus_2.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.minimize_btn.setIcon(icon1)
        self.minimize_btn.setIconSize(QtCore.QSize(15, 15))
        self.minimize_btn.setFlat(True)
        self.minimize_btn.setObjectName("minimize_btn")
        self.horizontalLayout_3.addWidget(self.minimize_btn)
        self.cls_btn = QtWidgets.QPushButton(self.cntrl_frm)
        self.cls_btn.setMinimumSize(QtCore.QSize(0, 26))
        self.cls_btn.setStyleSheet("\n"
"QPushButton{\n"
"color: rgb(255, 255, 255);\n"
"\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"\n"
"    background-color: rgb(255, 0, 0);\n"
"    border-style:inset;\n"
"\n"
"}")
        self.cls_btn.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/ii/images/white_x.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.cls_btn.setIcon(icon2)
        self.cls_btn.setIconSize(QtCore.QSize(24, 30))
        self.cls_btn.setFlat(True)
        self.cls_btn.setObjectName("cls_btn")
        self.horizontalLayout_3.addWidget(self.cls_btn)
        self.horizontalLayout.addWidget(self.cntrl_frm)
        self.verticalLayout.addWidget(self.top_bar)
        self.cont_1 = QtWidgets.QFrame(self.main)
        self.cont_1.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.cont_1.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.cont_1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.cont_1.setObjectName("cont_1")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.cont_1)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.nav_drw = QtWidgets.QFrame(self.cont_1)
        self.nav_drw.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nav_drw.sizePolicy().hasHeightForWidth())
        self.nav_drw.setSizePolicy(sizePolicy)
        self.nav_drw.setMinimumSize(QtCore.QSize(0, 560))
        self.nav_drw.setMaximumSize(QtCore.QSize(0, 560))
        self.nav_drw.setStyleSheet("background-color: rgb(4, 4, 4);")
        self.nav_drw.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.nav_drw.setFrameShadow(QtWidgets.QFrame.Raised)
        self.nav_drw.setObjectName("nav_drw")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.nav_drw)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.nav_mnu = QtWidgets.QFrame(self.nav_drw)
        self.nav_mnu.setMinimumSize(QtCore.QSize(0, 0))
        self.nav_mnu.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.nav_mnu.setStyleSheet("QFrame{background-color: rgb(4, 4, 4);}\n"
"\n"
"QPushButton{\n"
"padding: 10px 10px;\n"
"background-color: rgb(4, 4, 4);\n"
"color:#ffffff;\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"font-weight: bold;\n"
"font-size:12px;\n"
"}\n"
"\n"
"\n"
"QPushButton::pressed{\n"
"background-color: rgb(224, 255, 238);\n"
"    border-style:inset;\n"
"\n"
"}")
        self.nav_mnu.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.nav_mnu.setFrameShadow(QtWidgets.QFrame.Raised)
        self.nav_mnu.setObjectName("nav_mnu")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.nav_mnu)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.home = QtWidgets.QPushButton(self.nav_mnu)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.home.sizePolicy().hasHeightForWidth())
        self.home.setSizePolicy(sizePolicy)
        self.home.setMinimumSize(QtCore.QSize(70, 0))
        self.home.setMaximumSize(QtCore.QSize(210, 16777215))
        self.home.setStyleSheet("padding-left:70px;")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/ii/images/home.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.home.setIcon(icon3)
        self.home.setIconSize(QtCore.QSize(25, 25))
        self.home.setFlat(True)
        self.home.setObjectName("home")
        self.verticalLayout_4.addWidget(self.home)
        self.filtering = QtWidgets.QPushButton(self.nav_mnu)
        self.filtering.setStyleSheet("padding-left:70px;")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/ii/images/filter.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.filtering.setIcon(icon4)
        self.filtering.setIconSize(QtCore.QSize(25, 25))
        self.filtering.setFlat(True)
        self.filtering.setObjectName("filtering")
        self.verticalLayout_4.addWidget(self.filtering)
        self.about = QtWidgets.QPushButton(self.nav_mnu)
        self.about.setStyleSheet("padding-left:80px;")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/ii/images/info.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.about.setIcon(icon5)
        self.about.setIconSize(QtCore.QSize(25, 25))
        self.about.setFlat(True)
        self.about.setObjectName("about")
        self.verticalLayout_4.addWidget(self.about)
        self.verticalLayout_3.addWidget(self.nav_mnu)
        self.horizontalLayout_2.addWidget(self.nav_drw)
        self.pages_frm = QtWidgets.QFrame(self.cont_1)
        self.pages_frm.setMinimumSize(QtCore.QSize(800, 0))
        self.pages_frm.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.pages_frm.setStyleSheet("QFrame{background-color: rgb(4, 4, 4);}\n"
"\n"
"")
        self.pages_frm.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.pages_frm.setFrameShadow(QtWidgets.QFrame.Raised)
        self.pages_frm.setObjectName("pages_frm")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.pages_frm)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.main_pages_vwr = QtWidgets.QStackedWidget(self.pages_frm)
        self.main_pages_vwr.setMaximumSize(QtCore.QSize(900, 600))
        self.main_pages_vwr.setStyleSheet("background-color: rgb(0,0,0);")
        self.main_pages_vwr.setObjectName("main_pages_vwr")
        self.dicom_pg = QtWidgets.QWidget()
        self.dicom_pg.setStyleSheet("background-color:black;\n"
"\n"
"")
        self.dicom_pg.setObjectName("dicom_pg")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.dicom_pg)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.info_frame = QtWidgets.QFrame(self.dicom_pg)
        self.info_frame.setMaximumSize(QtCore.QSize(140, 16777215))
        self.info_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.info_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.info_frame.setObjectName("info_frame")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.info_frame)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.label_2 = QtWidgets.QLabel(self.info_frame)
        font = QtGui.QFont()
        font.setFamily("Buxton Sketch")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_11.addWidget(self.label_2)
        self.info_list = QtWidgets.QListWidget(self.info_frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.info_list.setFont(font)
        self.info_list.setStyleSheet("QListWidget{background-color: rgb(255, 255, 255);} QListWidget::item { border: 1px solid red; border-radius:2px; }\n"
"\n"
"border-style:outset;\n"
"border-radius:10px;")
        self.info_list.setObjectName("info_list")
        self.verticalLayout_11.addWidget(self.info_list)
        self.horizontalLayout_5.addWidget(self.info_frame)
        self.dicom_content = QtWidgets.QFrame(self.dicom_pg)
        font = QtGui.QFont()
        font.setFamily("Century")
        self.dicom_content.setFont(font)
        self.dicom_content.setStyleSheet("background-color: rgb(0,0,0);")
        self.dicom_content.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.dicom_content.setFrameShadow(QtWidgets.QFrame.Raised)
        self.dicom_content.setObjectName("dicom_content")
        self.gridLayout = QtWidgets.QGridLayout(self.dicom_content)
        self.gridLayout.setObjectName("gridLayout")
        self.axial_wid = QtWidgets.QWidget(self.dicom_content)
        self.axial_wid.setObjectName("axial_wid")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.axial_wid)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.axial_canvas = QtWidgets.QLabel(self.axial_wid)
        self.axial_canvas.setText("Axial")
        self.axial_canvas.setAlignment(Qt.AlignCenter)
        self.axial_canvas.setStyleSheet("background-color:rgb(195,199,199); font-weight:bold; font-size:24px; font-family:Caveat Brush;")
        self.axial_canvas.setObjectName("axial_canvas")
        self.axial_cord = QtWidgets.QLabel(self.axial_wid)
        self.axial_cord.setStyleSheet("background-color:black; font-weight:bold; font-size:14px; color:white;")
        self.axial_cord.setMaximumHeight(30)
        self.verticalLayout_14.addWidget(self.axial_canvas)
        self.verticalLayout_14.addWidget(self.axial_cord)
        self.gridLayout.addWidget(self.axial_wid, 0, 0, 1, 1)
        self.coronal_wid = QtWidgets.QWidget(self.dicom_content)
        self.coronal_wid.setObjectName("coronal_wid")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.coronal_wid)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.coronal_canvas = QtWidgets.QLabel(self.coronal_wid)
        self.coronal_canvas.setText("Coronal")
        self.coronal_canvas.setAlignment(Qt.AlignCenter)
        self.coronal_canvas.setStyleSheet("background-color: rgb(195,199,199);font-weight:bold; font-size:24px; font-family:Caveat Brush;")
        self.coronal_canvas.setObjectName("coronal_canvas")
        self.coronal_cord = QtWidgets.QLabel(self.coronal_wid)
        self.coronal_cord.setStyleSheet("background-color:black; font-weight:bold; font-size:14px; color:white;")
        self.coronal_cord.setMaximumHeight(30)
        self.verticalLayout_13.addWidget(self.coronal_canvas)
        self.verticalLayout_13.addWidget(self.coronal_cord)
        self.gridLayout.addWidget(self.coronal_wid, 0, 1, 1, 1)
        self.sagital_wid = QtWidgets.QWidget(self.dicom_content)
        self.sagital_wid.setObjectName("sagital_wid")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.sagital_wid)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.sagital_canvas = QtWidgets.QLabel(self.sagital_wid)
        self.sagital_canvas.setText("Sagittal")
        self.sagital_canvas.setAlignment(Qt.AlignCenter)
        self.sagital_canvas.setStyleSheet("background-color: rgb(195,199,199);font-weight:bold; font-size:24px; font-family:Caveat Brush;")
        self.sagital_canvas.setObjectName("sagital_canvas")
        self.sagital_cord = QtWidgets.QLabel(self.sagital_wid)
        self.sagital_cord.setStyleSheet("background-color:black; font-weight:bold; font-size:14px; color:white;")
        self.sagital_cord.setMaximumHeight(30)
        self.verticalLayout_12.addWidget(self.sagital_canvas)
        self.verticalLayout_12.addWidget(self.sagital_cord)
        self.gridLayout.addWidget(self.sagital_wid, 1, 0, 1, 1)
        self.control_wid = QtWidgets.QWidget(self.dicom_content)
        self.control_wid.setStyleSheet("background-color: black;\n"
"color: rgb(255, 255, 255);")
        self.control_wid.setObjectName("control_wid")
        self.slices_slider = QtWidgets.QSlider(self.control_wid)
        self.slices_slider.setGeometry(QtCore.QRect(10, 130, 341, 19))
        self.slices_slider.setOrientation(QtCore.Qt.Horizontal)
        self.slices_slider.setObjectName("slices_slider")
        self.slices_slider.setMinimum(00)
        self.slices_slider.setMaximum(100)
        self.sagital_tgl = QtWidgets.QCheckBox(self.control_wid)
        self.sagital_tgl.setGeometry(QtCore.QRect(30, 215, 70, 17))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.sagital_tgl.setFont(font)
        self.sagital_tgl.setStyleSheet("color: rgb(255, 255, 255);")
        self.sagital_tgl.setText("")
        self.sagital_tgl.setObjectName("sagital_tgl")
        self.coronal_tgl = QtWidgets.QCheckBox(self.control_wid)
        self.coronal_tgl.setGeometry(QtCore.QRect(30, 187, 70, 17))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.coronal_tgl.setFont(font)
        self.coronal_tgl.setStyleSheet("color: rgb(255, 255, 255);")
        self.coronal_tgl.setText("")
        self.coronal_tgl.setObjectName("coronal_tgl")
        self.axial_tgl = QtWidgets.QCheckBox(self.control_wid)
        self.axial_tgl.setGeometry(QtCore.QRect(30, 160, 70, 17))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.axial_tgl.setFont(font)
        self.axial_tgl.setStyleSheet("color: rgb(255, 255, 255);")
        self.axial_tgl.setText("")
        self.axial_tgl.setObjectName("axial_tgl")
        self.get_path_btn = QtWidgets.QPushButton(self.control_wid)
        self.get_path_btn.setGeometry(QtCore.QRect(140, 165, 181, 61))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.get_path_btn.setFont(font)
        self.get_path_btn.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.get_path_btn.setStyleSheet("QPushButton{\n"
"    background-color: rgb(47, 11, 255);\n"
"color: rgb(255, 255, 255);\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"    background-color: rgb(152, 223, 255);\n"
"color:black;\n"
" border-style:inset;\n"
"\n"
"}")
        self.get_path_btn.setObjectName("get_path_btn")
        self.sagital_lbl = QtWidgets.QLabel(self.control_wid)
        self.sagital_lbl.setGeometry(QtCore.QRect(50, 215, 54, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.sagital_lbl.setFont(font)
        self.sagital_lbl.setObjectName("sagital_lbl")
        self.coronal_lbl = QtWidgets.QLabel(self.control_wid)
        self.coronal_lbl.setGeometry(QtCore.QRect(50, 188, 51, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.coronal_lbl.setFont(font)
        self.coronal_lbl.setObjectName("coronal_lbl")
        self.axial_lbl = QtWidgets.QLabel(self.control_wid)
        self.axial_lbl.setGeometry(QtCore.QRect(50, 161, 47, 13))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.axial_lbl.setFont(font)
        self.axial_lbl.setObjectName("axial_lbl")
        self.img_lbl = QtWidgets.QLabel(self.control_wid)
        self.img_lbl.setGeometry(QtCore.QRect(230, 10, 121, 111))
        self.img_lbl.setText("")
        self.img_lbl.setPixmap(QtGui.QPixmap(":/ii/images/med.png"))
        self.img_lbl.setScaledContents(True)
        self.img_lbl.setObjectName("img_lbl")
        self.play_dicom_btn = QtWidgets.QPushButton(self.control_wid)
        self.play_dicom_btn.setGeometry(QtCore.QRect(120, 40, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.play_dicom_btn.setFont(font)
        self.play_dicom_btn.setText("Play")
        self.play_dicom_btn.setStyleSheet("QPushButton{\n"
"color: rgb(255, 255, 255);\n"
"    background-color:#016064;\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"background-color: rgb(224, 255, 238);\n"
"color:black;\n"
" border-style:inset;\n"
"\n"
"}")
        self.stop_dicom_btn = QtWidgets.QPushButton(self.control_wid)
        self.stop_dicom_btn.setGeometry(QtCore.QRect(120, 80, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.stop_dicom_btn.setFont(font)
        self.stop_dicom_btn.setText("Stop")
        self.stop_dicom_btn.setStyleSheet("QPushButton{\n"
"color: rgb(255, 255, 255);\n"
"    background-color:#A91B0D;\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"background-color: rgb(224, 255, 238);\n"
"color:black;\n"
" border-style:inset;\n"
"\n"
"}")
        self.save_dicom_btn = QtWidgets.QPushButton(self.control_wid)
        self.save_dicom_btn.setGeometry(QtCore.QRect(10, 40, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.save_dicom_btn.setFont(font)
        self.save_dicom_btn.setStyleSheet("QPushButton{\n"
"color: rgb(255, 255, 255);\n"
"    background-color: rgb(0, 148, 0);\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"background-color: rgb(224, 255, 238);\n"
"color:black;\n"
" border-style:inset;\n"
"\n"
"}")
        self.save_dicom_btn.setObjectName("save_dicom_btn")
        self.clear_dicom_btn = QtWidgets.QPushButton(self.control_wid)
        self.clear_dicom_btn.setGeometry(QtCore.QRect(10, 80, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.clear_dicom_btn.setFont(font)
        self.clear_dicom_btn.setStyleSheet("QPushButton{\n"
"color: rgb(255, 255, 255);\n"
"    background-color: rgb(195, 11, 146);\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"background-color: rgb(224, 255, 238);\n"
"color:black;\n"
" border-style:inset;\n"
"\n"
"}")
        self.clear_dicom_btn.setObjectName("clear_dicom_btn")
        self.gridLayout.addWidget(self.control_wid, 1, 1, 1, 1)
        self.horizontalLayout_5.addWidget(self.dicom_content)
        self.main_pages_vwr.addWidget(self.dicom_pg)
        self.Filters_pg = QtWidgets.QWidget()
        self.Filters_pg.setStyleSheet("background-color: rgb(4, 4, 4);")
        self.Filters_pg.setObjectName("Filters_pg")
        self.photo_wid = QtWidgets.QWidget(self.Filters_pg)
        self.photo_wid.setGeometry(QtCore.QRect(91, 60, 300, 321))
        self.photo_view = QtWidgets.QGridLayout(self.photo_wid)
        self.photo_view.setContentsMargins(0, 0, 0, 0)
        self.view=Image_Drag_Drop()
        self.photo_view.addWidget(self.view,0,0,0,0)
        
        self.clear_img_btn = QtWidgets.QPushButton(self.Filters_pg)
        self.clear_img_btn.setGeometry(QtCore.QRect(300, 400, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.clear_img_btn.setFont(font)
        self.clear_img_btn.setStyleSheet("QPushButton{\n"
"color: rgb(255, 255, 255);\n"
"    background-color: rgb(195, 11, 146);\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"background-color: rgb(224, 255, 238);\n"
"color:black;\n"
" border-style:inset;\n"
"\n"
"}")
        self.clear_img_btn.setObjectName("clear_img_btn")
        self.save_img_btn = QtWidgets.QPushButton(self.Filters_pg)
        self.save_img_btn.setGeometry(QtCore.QRect(90, 400, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.save_img_btn.setFont(font)
        self.save_img_btn.setStyleSheet("QPushButton{\n"
"color: rgb(255, 255, 255);\n"
"    background-color: rgb(0, 148, 0);\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"background-color: rgb(224, 255, 238);\n"
"color:black;\n"
" border-style:inset;\n"
"\n"
"}")
        self.save_img_btn.setObjectName("save_img_btn")
        self.frame = QtWidgets.QFrame(self.Filters_pg)
        self.frame.setGeometry(QtCore.QRect(570, 100, 300, 381))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.filters_drw = QtWidgets.QFrame(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filters_drw.sizePolicy().hasHeightForWidth())
        self.filters_drw.setSizePolicy(sizePolicy)
        self.filters_drw.setMinimumSize(QtCore.QSize(280, 0))
        self.filters_drw.setMaximumSize(QtCore.QSize(210, 0))
        self.filters_drw.setStyleSheet("background-color: rgb(4, 4, 4);")
        self.filters_drw.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.filters_drw.setFrameShadow(QtWidgets.QFrame.Raised)
        self.filters_drw.setObjectName("filters_drw")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.filters_drw)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.filters_mnu = QtWidgets.QScrollArea(self.filters_drw)
        self.filters_mnu.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.filters_mnu.setStyleSheet("QFrame{background-color: rgb(4, 4, 4);}\n"
"\n"
"QPushButton{\n"
"padding: 10px 10px;\n"
"background-color: rgb(255, 255, 255);\n"
"color:black;\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"font-weight: bold;\n"
"font-size:12px;\n"
"}\n"
"\n"
"\n"
"QPushButton::pressed{\n"
"background-color: rgb(224, 255, 238);\n"
"    border-style:inset;\n"
"\n"
"}\n"
"\n"
"QScrollArea{border-style:none;}\n"
"\n"
" QScrollBar:vertical\n"
" {\n"
"     height: 15px;\n"
"     margin: 3px 15px 3px 15px;\n"
"     border: 1px transparent #2A2929;\n"
"     border-radius: 4px;\n"
"     background-color: yellow;    /* #2A2929; */\n"
" }\n"
" QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical\n"
" {\n"
"     background: none;\n"
" }")
        self.filters_mnu.setWidgetResizable(True)
        self.filters_mnu.setAlignment(QtCore.Qt.AlignCenter)
        self.filters_mnu.setObjectName("filters_mnu")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 260, 236))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setSpacing(10)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.blur_btn = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.blur_btn.sizePolicy().hasHeightForWidth())
        self.blur_btn.setSizePolicy(sizePolicy)
        self.blur_btn.setMinimumSize(QtCore.QSize(70, 0))
        self.blur_btn.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(1)
        font.setBold(True)
        font.setWeight(75)
        self.blur_btn.setFont(font)
        self.blur_btn.setStyleSheet("\n"
"Font-size:15px;")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/ii/images/edge.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.blur_btn.setIcon(icon6)
        self.blur_btn.setIconSize(QtCore.QSize(40, 40))
        self.blur_btn.setFlat(True)
        self.blur_btn.setObjectName("blur_btn")
        self.verticalLayout_7.addWidget(self.blur_btn)
        self.threshold_btn = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.threshold_btn.setMaximumSize(QtCore.QSize(16777215, 40))
        self.threshold_btn.setStyleSheet("\n"
"Font-size:15px;")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/ii/images/binary.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.threshold_btn.setIcon(icon7)
        self.threshold_btn.setIconSize(QtCore.QSize(25, 25))
        self.threshold_btn.setObjectName("threshold_btn")
        self.verticalLayout_7.addWidget(self.threshold_btn)
        self.negative_btn = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.negative_btn.setStyleSheet("font-size:15px;")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/ii/images/invert.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.negative_btn.setIcon(icon8)
        self.negative_btn.setIconSize(QtCore.QSize(20, 20))
        self.negative_btn.setObjectName("negative_btn")
        self.verticalLayout_7.addWidget(self.negative_btn)
        self.filters_mnu.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_6.addWidget(self.filters_mnu)
        self.verticalLayout_8.addWidget(self.filters_drw)
        self.effects_btn = QtWidgets.QPushButton(self.Filters_pg)
        self.effects_btn.setGeometry(QtCore.QRect(570, 40, 290, 41))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.effects_btn.setFont(font)
        self.effects_btn.setStyleSheet("QPushButton{\n"
"color: rgb(0, 0, 0);\n"
"    background-color:rgb(255, 255, 255);\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"background-color: rgb(224, 255, 238);\n"
"color:purple;\n"
" border-style:inset;\n"
"\n"
"}")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/ii/images/effects.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.effects_btn.setIcon(icon9)
        self.effects_btn.setIconSize(QtCore.QSize(30, 30))
        self.effects_btn.setObjectName("effects_btn")
        self.frame_sld = QtWidgets.QFrame(self.Filters_pg)
        self.frame_sld.setGeometry(QtCore.QRect(460, 90, 84, 391))
        self.frame_sld.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_sld.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_sld.setObjectName("frame_sld")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.frame_sld)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.filters_sliders = QtWidgets.QFrame(self.frame_sld)
        self.filters_sliders.setMaximumSize(QtCore.QSize(16777215, 0))
        self.filters_sliders.setStyleSheet("")
        self.filters_sliders.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.filters_sliders.setFrameShadow(QtWidgets.QFrame.Raised)
        self.filters_sliders.setObjectName("filters_sliders")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.filters_sliders)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.blur_sld = QtWidgets.QSlider(self.filters_sliders)
        self.blur_sld.setOrientation(QtCore.Qt.Vertical)
        self.blur_sld.setObjectName("blur_sld")
        self.horizontalLayout_4.addWidget(self.blur_sld)
        self.bright_sld = QtWidgets.QSlider(self.filters_sliders)
        self.bright_sld.setOrientation(QtCore.Qt.Vertical)
        self.bright_sld.setObjectName("bright_sld")
        self.horizontalLayout_4.addWidget(self.bright_sld)
        self.verticalLayout_9.addWidget(self.filters_sliders)
        self.brightness_lbl = QtWidgets.QLabel(self.Filters_pg)
        self.brightness_lbl.setGeometry(QtCore.QRect(510, 50, 31, 31))
        self.brightness_lbl.setText("")
        self.brightness_lbl.setPixmap(QtGui.QPixmap(":/ii/images/brightness.png"))
        self.brightness_lbl.setScaledContents(True)
        self.brightness_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.brightness_lbl.setObjectName("brightness_lbl")
        self.blur_lbl = QtWidgets.QLabel(self.Filters_pg)
        self.blur_lbl.setGeometry(QtCore.QRect(460, 50, 31, 31))
        self.blur_lbl.setText("")
        self.blur_lbl.setPixmap(QtGui.QPixmap(":/ii/images/blur.png"))
        self.blur_lbl.setScaledContents(True)
        self.blur_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.blur_lbl.setObjectName("blur_lbl")
        self.get_img_btn = QtWidgets.QPushButton(self.Filters_pg)
        self.get_img_btn.setGeometry(QtCore.QRect(195, 400, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.get_img_btn.setFont(font)
        self.get_img_btn.setStyleSheet("QPushButton{\n"
"    background-color: rgb(47, 11, 255);\n"
"color: rgb(255, 255, 255);\n"
"border-style:outset;\n"
"border-radius:10px;\n"
"}\n"
"\n"
"QPushButton::pressed{\n"
"    background-color: rgb(152, 223, 255);\n"
"color:black;\n"
" border-style:inset;\n"
"\n"
"}")
        self.get_img_btn.setObjectName("get_img_btn")
        self.main_pages_vwr.addWidget(self.Filters_pg)
        self.About_pg = QtWidgets.QWidget()
        self.About_pg.setStyleSheet("background-color: rgb(36, 36, 36);")
        self.About_pg.setObjectName("About_pg")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.About_pg)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.frame_2 = QtWidgets.QFrame(self.About_pg)
        self.frame_2.setStyleSheet("color: rgb(255, 255, 255);")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.label_7 = QtWidgets.QLabel(self.frame_2)
        self.label_7.setText("")
        self.label_7.setObjectName("label_7")
        self.verticalLayout_10.addWidget(self.label_7)
        self.label_5 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setFamily("Caveat Brush")
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_10.addWidget(self.label_5)
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setFamily("Caveat Brush")
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_10.addWidget(self.label_4)
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setFamily("Caveat Brush")
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_10.addWidget(self.label_3)
        self.label_6 = QtWidgets.QLabel(self.frame_2)
        self.label_6.setText("")
        self.label_6.setObjectName("label_6")
        self.verticalLayout_10.addWidget(self.label_6)
        self.horizontalLayout_6.addWidget(self.frame_2)
        self.label = QtWidgets.QLabel(self.About_pg)
        self.label.setMaximumSize(QtCore.QSize(600, 600))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/ii/images/hh.jpg"))
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_6.addWidget(self.label)
        self.main_pages_vwr.addWidget(self.About_pg)
        self.verticalLayout_5.addWidget(self.main_pages_vwr)
        self.horizontalLayout_2.addWidget(self.pages_frm)
        self.verticalLayout.addWidget(self.cont_1)
        DICOM.setCentralWidget(self.main)

        self.retranslateUi(DICOM)
        self.main_pages_vwr.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DICOM)

    def retranslateUi(self, DICOM):
        _translate = QtCore.QCoreApplication.translate
        DICOM.setWindowTitle(_translate("DICOM", "MainWindow"))
        self.home.setText(_translate("DICOM", "Home"))
        self.filtering.setText(_translate("DICOM", "Filters"))
        self.about.setText(_translate("DICOM", "About"))
        self.label_2.setText(_translate("DICOM", "Information"))
        self.get_path_btn.setText(_translate("DICOM", "Get Path"))
        self.sagital_lbl.setText(_translate("DICOM", "Saggital"))
        self.coronal_lbl.setText(_translate("DICOM", "Coronal"))
        self.axial_lbl.setText(_translate("DICOM", "Axial"))
        self.save_dicom_btn.setText(_translate("DICOM", "Save"))
        self.clear_dicom_btn.setText(_translate("DICOM", "Reset"))
        self.clear_img_btn.setText(_translate("DICOM", "Clear"))
        self.save_img_btn.setText(_translate("DICOM", "Save"))
        self.blur_btn.setText(_translate("DICOM", "Edge"))
        self.threshold_btn.setText(_translate("DICOM", "Threshold"))
        self.negative_btn.setText(_translate("DICOM", "Invert"))
        self.effects_btn.setText(_translate("DICOM", "Effects"))
        self.get_img_btn.setText(_translate("DICOM", "Get"))
        self.label_5.setText(_translate("DICOM", "Yusuf Hamdy Mahmoud Harb"))
        self.running=False

##########################################################################################
        #Connection Section

        self.tgl_btn.clicked.connect(lambda:ac.Interface_actions.menu_slide(self))
        self.cls_btn.clicked.connect(lambda:ac.Interface_actions.Close(self))
        self.minimize_btn.clicked.connect(lambda:ac.Interface_actions.minimize(self))

        self.filtering.clicked.connect(lambda:ac.Interface_actions.change_page(self,1))
        self.home.clicked.connect(lambda:ac.Interface_actions.change_page(self,0))
        self.about.clicked.connect(lambda:ac.Interface_actions.change_page(self,2))

        self.effects_btn.clicked.connect(lambda:ac.Interface_actions.show_filters(self))
        self.threshold_btn.clicked.connect(lambda: self.view.threshold(file_path))
        self.negative_btn.clicked.connect(lambda: self.view.invert(file_path))
        self.blur_btn.clicked.connect(lambda:self.view.edge_image(file_path))
        self.blur_sld.valueChanged['int'].connect(self.view.blur_value)
        self.bright_sld.valueChanged['int'].connect(self.view.brightness_value)
        self.clear_img_btn.clicked.connect(lambda:self.view.clear_image())
        self.save_img_btn.clicked.connect(lambda:self.view.save_image(filtered))
        self.get_img_btn.clicked.connect(self.get_dicom_img)

        self.get_path_btn.clicked.connect(self.get_dicom_path)
        self.save_dicom_btn.clicked.connect(self.save_dicom_window)
        self.clear_dicom_btn.clicked.connect(self.reset_dcm)
        self.play_dicom_btn.clicked.connect(self.ceni_mode)
        self.stop_dicom_btn.clicked.connect(self.stop_slices)
        self.slices_slider.valueChanged['int'].connect(self.view_dicom_slices)
        self.axial_canvas.setMouseTracking(True)
        self.axial_canvas.mouseMoveEvent=self.AxgetPos
        self.coronal_canvas.setMouseTracking(True)
        self.coronal_canvas.mouseMoveEvent=self.CogetPos
        self.sagital_canvas.setMouseTracking(True)
        self.sagital_canvas.mouseMoveEvent=self.SggetPos
##########################################################################################

#Dicom functions section

    def get_dicom_img(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', '',
                                        'All Files (*.dcm)')
        if path != ('', ''):
            global file_path
            file_path=path[0]
            self.view.set_dicom_img(file_path)






    def reset_dcm(self):
        global planes_list,dicom_info,glob_cine_counter,p_space
        planes_list=[]
        dicom_info=[]
        self.slices_slider.setValue(0)
        self.running = False
        self.axial_canvas.clear()
        self.coronal_canvas.clear()
        self.sagital_canvas.clear()
        self.axial_cord.clear()
        self.coronal_cord.clear()
        self.sagital_cord.clear()
        self.info_list.clear()
        self.axial_canvas.setText("Axial")
        self.coronal_canvas.setText("Coronal")
        self.sagital_canvas.setText("Sagital")
        self.axial_tgl.setChecked(False)
        self.sagital_tgl.setChecked(False)
        self.coronal_tgl.setChecked(False)
        glob_cine_counter=0
        p_space=0









    def get_dicom_path(self):
        global folder_path,planes_list,dicom_info,p_space
        try:
            #Restarting and cleaning all the data and settings if there is any cached data before
            self.reset_dcm()
            path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            folder_path=path
            if path != "":
                ct_images=os.listdir(folder_path)
                slices = [pydicom.dcmread(folder_path+'/'+s,force=True) for s in ct_images]

                #Sorting by the z coordinate, ImagePositionPatient returns x,y,z coordinates
                slices = sorted(slices,key=lambda x:x.ImagePositionPatient[2])

                #Sorting by location
                #slices = sorted(slices,key=lambda x:x.SliceLocation)

                img_shape = list(slices[0].pixel_array.shape)
                img_shape.append(len(slices))
                volume3d=np.zeros(img_shape)

                p_space=slices[0].PixelSpacing

                # cor=0
                # sag=0
                #for showing loading dialog
                self.load_slices=QtWidgets.QProgressDialog("Loading Process...",None,0,len(slices),self)
                self.load_slices.setWindowTitle("Please Wait")
                self.load_slices.show()
                for i, s in enumerate(slices):
                    self.load_slices.setValue(i)
                    QtWidgets.qApp.processEvents()
                    img2d = s.pixel_array #axial
                    volume3d[:,:,i] = img2d
                    # cor = cor-1
                    # sag = sag-1
                    cor=(img_shape[0]-1)-i
                    sag=(img_shape[1]-1)-i
                    axial_slc=volume3d[:,:,i]
                    sagittal_slc=np.flipud(volume3d[:,sag,:].T)
                    coronal_slc=np.flipud(volume3d[cor,:,:].T)
                    # #if Sort using slicelocation
                    # sagittal_slc=volume3d[:,sag,:].T
                    # coronal_slc=volume3d[cor,:,:].T
                    planes_list.append((axial_slc,coronal_slc,sagittal_slc))
                    dicom_info.append([
                        "Patient Name:\n"+str(s.PatientName),
                        "Patient ID:\n"+str(s.PatientID),
                        "Patient Sex:\n"+str(s.PatientSex),
                        "Patient Age:\n"+str(s.PatientAge),
                        "Patient Weight:\n"+str(s.PatientWeight),

                        "Modality:\n"+str(s.Modality),
                        "Manufacturer:\n"+str(s.Manufacturer),
                        "M. Model Name:\n"+str(s.ManufacturerModelName),
                        "Inst. Name:\n"+str(s.InstitutionName),

                        "Rows:\n"+str(s.Rows),
                        "Columns:\n"+str(s.Columns),
                        "Pixel Spacing:\n"+str([round(x,2) for x in s.PixelSpacing]),
                        "Img Orient.:\n"+str(s.ImageOrientationPatient),
                        "Slice Location:\n"+str(s.SliceLocation),
                        
                    
                                      ])
                self.slices_slider.setMaximum(len(slices)-1)
                self.load_slices.hide()
            else:
                self.reset_dcm()


        #Exception If the user choose the wrong folder
        except Exception as e:
            #print(e)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Invalid Folder")
            msg.setInformativeText("Please make sure that the folder includes DICOM files")
            msg.setWindowTitle("DICOM lOAD")
            msg.exec_()
            folder_path=None
            planes_list=[]
            




                        

    def view_dicom_slices(self,val):
        if len(planes_list)<1:
            pass
        else:

            #For sliding through axial slices only
            if self.axial_tgl.isChecked() and not self.coronal_tgl.isChecked() and not self.sagital_tgl.isChecked():
                plane=planes_list[int(val)][0]
                resized_plane=cv2.resize(plane, dsize=(337,200), interpolation=cv2.INTER_CUBIC)
                img=imgia.array2qimage(resized_plane/resized_plane.max()*255)
                self.axial_canvas.setPixmap(QtGui.QPixmap.fromImage(img))   
                self.info_list.clear()
                self.info_list.addItems(dicom_info[int(val)])
                

            #For sliding through coronal slices only
            elif not self.axial_tgl.isChecked() and self.coronal_tgl.isChecked() and not self.sagital_tgl.isChecked():
                plane=planes_list[int(val)][1]
                resized_plane=cv2.resize(plane, dsize=(337,200), interpolation=cv2.INTER_CUBIC)
                img=imgia.array2qimage(resized_plane/resized_plane.max()*255)
                self.coronal_canvas.setPixmap(QtGui.QPixmap.fromImage(img))
                self.info_list.clear()
                self.info_list.addItems(dicom_info[int(val)])

            #For sliding through sagittal slices only
            elif not self.axial_tgl.isChecked() and not self.coronal_tgl.isChecked() and self.sagital_tgl.isChecked():
                plane=planes_list[int(val)][2]
                resized_plane=cv2.resize(plane, dsize=(337,200), interpolation=cv2.INTER_CUBIC)
                img=imgia.array2qimage(resized_plane/resized_plane.max()*255)
                self.sagital_canvas.setPixmap(QtGui.QPixmap.fromImage(img))
                self.info_list.clear()
                self.info_list.addItems(dicom_info[int(val)])
            
            #For sliding through axial-coronal slices only
            elif self.axial_tgl.isChecked() and self.coronal_tgl.isChecked() and not self.sagital_tgl.isChecked():
                plane=planes_list[int(val)][0]
                resized_plane=cv2.resize(plane, dsize=(337,200), interpolation=cv2.INTER_CUBIC)
                img=imgia.array2qimage(resized_plane/resized_plane.max()*255)
                self.axial_canvas.setPixmap(QtGui.QPixmap.fromImage(img))

                plane1=planes_list[int(val)][1]
                resized_plane1=cv2.resize(plane1, dsize=(337,200), interpolation=cv2.INTER_CUBIC)
                img1=imgia.array2qimage(resized_plane1/resized_plane1.max()*255)
                self.coronal_canvas.setPixmap(QtGui.QPixmap.fromImage(img1))
                self.info_list.clear()
                self.info_list.addItems(dicom_info[int(val)])


            #For sliding through axial-sagittal slices only
            elif self.axial_tgl.isChecked() and not self.coronal_tgl.isChecked() and self.sagital_tgl.isChecked():
                plane=planes_list[int(val)][0]
                resized_plane=cv2.resize(plane, dsize=(337,200), interpolation=cv2.INTER_CUBIC)
                img=imgia.array2qimage(resized_plane/resized_plane.max()*255)
                self.axial_canvas.setPixmap(QtGui.QPixmap.fromImage(img))

                plane2=planes_list[int(val)][2]
                resized_plane2=cv2.resize(plane2, dsize=(337,200), interpolation=cv2.INTER_CUBIC)
                img2=imgia.array2qimage(resized_plane2/resized_plane2.max()*255)
                self.sagital_canvas.setPixmap(QtGui.QPixmap.fromImage(img2))
                self.info_list.clear()
                self.info_list.addItems(dicom_info[int(val)])


            #For sliding through coronal-sagittal slices only
            elif not self.axial_tgl.isChecked() and self.coronal_tgl.isChecked() and self.sagital_tgl.isChecked():
                plane1=planes_list[int(val)][1]
                resized_plane1=cv2.resize(plane1, dsize=(337,200), interpolation=cv2.INTER_CUBIC)
                img1=imgia.array2qimage(resized_plane1/resized_plane1.max()*255)
                self.coronal_canvas.setPixmap(QtGui.QPixmap.fromImage(img1))

                plane2=planes_list[int(val)][2]
                resized_plane2=cv2.resize(plane2, dsize=(337,200), interpolation=cv2.INTER_CUBIC)
                img2=imgia.array2qimage(resized_plane2/resized_plane2.max()*255)
                self.sagital_canvas.setPixmap(QtGui.QPixmap.fromImage(img2))
                self.info_list.clear()
                self.info_list.addItems(dicom_info[int(val)])
            
            #For sliding through all slices
            elif self.axial_tgl.isChecked() and self.coronal_tgl.isChecked() and self.sagital_tgl.isChecked():
                plane=planes_list[int(val)][0]
                resized_plane=cv2.resize(plane, dsize=(337,200), interpolation=cv2.INTER_CUBIC)
                img=imgia.array2qimage(resized_plane/resized_plane.max()*255)
                self.axial_canvas.setPixmap(QtGui.QPixmap.fromImage(img))

                plane1=planes_list[int(val)][1]
                resized_plane1=cv2.resize(plane1, dsize=(337,200), interpolation=cv2.INTER_CUBIC)
                img1=imgia.array2qimage(resized_plane1/resized_plane1.max()*255)
                self.coronal_canvas.setPixmap(QtGui.QPixmap.fromImage(img1))

                plane2=planes_list[int(val)][2]
                resized_plane2=cv2.resize(plane2, dsize=(337,200), interpolation=cv2.INTER_CUBIC)
                img2=imgia.array2qimage(resized_plane2/resized_plane2.max()*255)
                self.sagital_canvas.setPixmap(QtGui.QPixmap.fromImage(img2))

                self.info_list.clear()
                self.info_list.addItems(dicom_info[int(val)])


    
    def ceni_mode(self):
        if len(planes_list)<1:
            pass
        else:
            self.play_dicom_btn.setDisabled(True)
            self.running = True
            global glob_cine_counter
            while self.running:
                self.slices_slider.setValue(glob_cine_counter)
                QtWidgets.qApp.processEvents()
                time.sleep(0.05)
                glob_cine_counter+=1
                if glob_cine_counter==len(planes_list):
                    glob_cine_counter=0
                    break
                    
            self.play_dicom_btn.setDisabled(False)
            self.running=False

    def stop_slices(self):
        self.running = False

    def save_dicom_window(self):
        screen = QtWidgets.QApplication.primaryScreen()
        winid = QtWidgets.QApplication.focusWindow().winId()
        pixmap = screen.grabWindow(winid)
        ba = QtCore.QByteArray()
        buff = QtCore.QBuffer(ba)
        pixmap.save(buff, "PNG")
        pi= QtGui.QPixmap()
        pi.loadFromData(ba.data())
        pi.save("dicom_window/img"+str(random.randint(0,9999))+".png","PNG")


########################################################################################## 

#for calculating distance and getting coordinates section
    def AxgetPos(self , event):
        global planes_list,p_space
        if len(planes_list)>0 and self.axial_tgl.isChecked():

            x = event.pos().x()
            y = event.pos().y()
            x_distance=round(x*p_space[0],1)
            y_distance=round(y*p_space[1],1)
            self.axial_cord.setText("A:(X:"+str(x)+", Y:"+str(y)+")"+
                                    "/(X:"+str(x_distance)+"mm, Y:"+str(y_distance)+"mm)")

    def CogetPos(self , event):
        global planes_list,p_space
        if len(planes_list)>0 and self.coronal_tgl.isChecked():

            x = event.pos().x()
            y = event.pos().y()
            x_distance=round(x*p_space[0],1)
            y_distance=round(y*p_space[1],1)
            self.coronal_cord.setText("C:(X:"+str(x)+", Y:"+str(y)+")"+
                                    "/(X:"+str(x_distance)+"mm, Y:"+str(y_distance)+"mm)")


    def SggetPos(self , event):
        global planes_list,p_space
        if len(planes_list)>0 and self.sagital_tgl.isChecked():

            x = event.pos().x()
            y = event.pos().y()
            x_distance=round(x*p_space[0],1)
            y_distance=round(y*p_space[1],1)
            self.sagital_cord.setText("S:(X:"+str(x)+", Y:"+str(y)+")"+
                                    "/(X:"+str(x_distance)+"mm, Y:"+str(y_distance)+"mm)")
        
            
            
##########################################################################################                
            

        

import images
import interface_actions as ac

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    plane=ac.Interface_actions()
    plane.show()
    sys.exit(app.exec_())

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#############################################################################
##
## Copyright (c) 2016, gamesun
## All right reserved.
##
## This file is part of SuperDbg.
##
## SuperDbg is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## SuperDbg is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with SuperDbg.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################


"""
the main module running as window.
"""

#system imports
import sys, os
import ntpath

#pyqt imports
from PyQt4 import QtCore,QtGui,QtSvg
from PyQt4.QtCore import Qt

#converter imports
#from convert import ConvertFormat, ParserList
#from make_svg import MakeSvg
#from make_xhtml import MakeXhtml
#from make_text import MakeText

import zipfile
import appInfo

#from parentInfo import getParentInfo

import re
re_findVariables = re.compile('(?P<label>\w+)\s+0x(?P<addr>[0-9a-fA-F]{8})' \
'\s+Data\s+(?P<len>[0-9]+)\s+(?P<section>[0-9a-zA-Z\(\)\._]+)')

SVG_CPY2CLIPBOARD="""<svg version="1.0" xmlns="http://www.w3.org/2000/svg" 
width="20" height="20" viewBox="0 0 64 64" preserveAspectRatio="xMidYMid meet">
<g transform="translate(0,64) scale(0.1,-0.10)" fill="#000000" stroke="none">
<path d="M237 598 c-9 -7 -21 -25 -26 -40 -10 -27 -13 -28 -81 -28 -64 0 -71
-2 -78 -22 -11 -33 -7 -467 5 -479 6 -6 97 -8 234 -7 l224 3 3 53 c3 47 1 53
-15 50 -13 -2 -18 -13 -18 -38 l0 -35 -200 0 -200 0 0 180 0 180 200 0 200 0
1 -45 c2 -67 3 -70 19 -70 13 0 15 17 13 113 l-3 112 -73 3 c-58 2 -74 6 -79
20 -19 54 -85 80 -126 50z m91 -68 c9 -25 16 -30 42 -30 39 0 70 -16 70 -35 0
-13 -26 -15 -155 -15 -129 0 -155 2 -155 15 0 19 31 35 70 35 24 0 33 6 41 28
22 59 67 61 87 2z"/>
<path d="M130 355 c0 -12 17 -15 95 -15 78 0 95 3 95 15 0 12 -17 15 -95 15
-78 0 -95 -3 -95 -15z"/>
<path d="M342 268 l-52 -54 54 -53 55 -54 3 34 3 34 98 3 97 3 0 34 0 34 -97
3 -98 3 -5 33 -5 33 -53 -53z"/>
<path d="M130 275 c0 -11 12 -15 45 -15 33 0 45 4 45 15 0 11 -12 15 -45 15
-33 0 -45 -4 -45 -15z"/>
<path d="M130 195 c0 -11 12 -15 45 -15 33 0 45 4 45 15 0 11 -12 15 -45 15
-33 0 -45 -4 -45 -15z"/>
<path d="M127 123 c-18 -17 0 -23 73 -23 64 0 80 3 80 15 0 12 -15 15 -73 15
-41 0 -77 -3 -80 -7z"/>
</g></svg>"""

#try:
#    _fromUtf8 = QtCore.QString.fromUtf8
#except AttributeError:
#    def _fromUtf8(s):
#        return s

class BtnTitlebar(QtGui.QPushButton):
    def __init__(self, *args, **kwargs):
        super(BtnTitlebar, self).__init__(*args, **kwargs)
        self.m_ishover = False
        
    def paintEvent(self, evt):
        super(BtnTitlebar, self).paintEvent(evt)
        
    def isHover(self):
        return self.m_ishover
        
    def enterEvent(self, evt):
        self.m_ishover = True
        
    def leaveEvent(self, evt):
        self.m_ishover = False

class BtnMinimize(BtnTitlebar):
    def __init__(self, *args, **kwargs):
        super(BtnMinimize, self).__init__(*args, **kwargs)
        
    def paintEvent(self, evt):
        super(BtnMinimize, self).paintEvent(evt)
        painter = QtGui.QPainter(self)
        if self.isDown() or self.isHover():
            painter.fillRect(QtCore.QRect(10,14,8,2), QtGui.QColor("#FFFFFF"))
        else:
            painter.fillRect(QtCore.QRect(10,14,8,2), QtGui.QColor("#282828"))

class BtnClose(BtnTitlebar):
    def __init__(self, *args, **kwargs):
        super(BtnClose, self).__init__(*args, **kwargs)
        
    def paintEvent(self, evt):
        super(BtnClose, self).paintEvent(evt)
        painter = QtGui.QPainter(self)
        if self.isDown() or self.isHover():
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor("#FFFFFF")), 1.42))
        else:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor("#282828")), 1.42))
        
        painter.drawLine(15,10,20,15)
        painter.drawPoint(14,9)
        painter.drawPoint(21,15)
        
        painter.drawLine(20,10,15,15)
        painter.drawPoint(21,9)
        painter.drawPoint(14,15)

class EditDrop(QtGui.QLineEdit):
    def __init__(self, *args, **kwargs):
        super(EditDrop, self).__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, evt):
        if evt.mimeData().hasUrls():
            evt.accept()
        else:
            evt.ignore()

    def dropEvent(self, evt):
        if evt.mimeData().hasUrls():
            #print evt.mimeData().urls()[0]
            url = evt.mimeData().urls()[0].toLocalFile()    # get first url
            #print url
            self.setText(url)        # assign first url to editline

class SVGPushButton(QtGui.QPushButton):
    def __init__(self, *args, **kwargs):
        super(SVGPushButton, self).__init__(*args, **kwargs)
        
        #self.setLayout(QtGui.QHBoxLayout())
        #self.layout().setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)

    def addPixmap(self, pixmap):
        self.pix=pixmap

    def paintEvent(self, evt):
        super(SVGPushButton, self).paintEvent(evt)
        painter = QtGui.QPainter(self)
        painter.drawPixmap(1, 1, 20, 20, self.pix)

    def enterEvent(self, evt):
        super(SVGPushButton, self).enterEvent(evt)
        QtGui.QToolTip.showText(self.parent().mapToGlobal(self.pos())+QtCore.QPoint(25,-21), "copy to clipboard")
        
#class TabCtrl(QtGui.QWidget):
#    def __init__(self, *args, **kwargs):
#        super(TabCtrl, self).__init__(*args, **kwargs)
#
#    def 

class MainWindow(QtGui.QWidget):
    def __init__(self, argv):

        QtGui.QWidget.__init__(self)

        # initial position
        self.m_DragPosition=self.pos()
        self.m_drag = False
        
        self.resize(552,245+34)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        #self.setStyleSheet("QWidget{background-color:#99d9ea;}")
        #self.setStyleSheet("QWidget{background-color:#99d9ea;}")
        
        self.setWindowTitle(appInfo.title)
        
        self.scriptPath = os.path.dirname(os.path.realpath(argv[0]))
        input_file_path = (len(argv) > 1) and argv[1].decode("cp932") or u""
        
        zf = zipfile.ZipFile("%s/library.zip" % (self.scriptPath))
        pix16 = QtGui.QPixmap()
        pix16.loadFromData(zf.read("media/16.png"), "png")
        pix32 = QtGui.QPixmap()
        pix32.loadFromData(zf.read("media/32.png"), "png")
        
#        pixcpy = QtGui.QPixmap()
#        pixcpy.loadFromData(zf.read("media/copy2clipboard.png"), "png")
        ico_pixcpy = QtGui.QIcon(self.scriptPath + "/media/copy2clipboard.svg")
        #pixcpy.loadFromData(zf.read("media/copy2clipboard.png"), "png")
        

        self.setWindowIcon(QtGui.QIcon(pix16))
        
        # add widgets
        qlbl_title = QtGui.QLabel(u"%s %s" % (appInfo.title, appInfo.version), self)
        qlbl_title.setGeometry(0,0,552,34)
        qlbl_title.setStyleSheet("QLabel{background-color:#30a7b8;"
                                        "border:none;"
                                        "color:#efefef;"
                                        "font:bold;"
                                        "font-size:16px;"
                                        "font-family:Microsoft YaHei;"
                                        "qproperty-alignment:AlignCenter;}")
        
        qlbl_ico = QtGui.QLabel(self)
        qlbl_ico.setGeometry(8,1,32,32)
        #qlbl_ico.setPixmap(pix32)
        #qlbl_ico.setWidget(qsvg)
        qlbl_ico.setStyleSheet("background-color:#30a7b8;")
        
        self.qbtn_minimize=BtnMinimize(self)
        self.qbtn_minimize.setGeometry(476,0,28,24)
        self.qbtn_minimize.setStyleSheet("QPushButton{background-color:#30a7b8;"
                                                      "border:none;"
#                                                      "color:#000000;"
                                                      "font-size:12px;"
                                                      "font-family:Tahoma;}"
                                        "QPushButton:hover{background-color:#227582;}"
                                        "QPushButton:pressed{background-color:#14464e;}")
        
        self.qbtn_close=BtnClose(self)
        self.qbtn_close.setGeometry(505,0,36,24)
        self.qbtn_close.setStyleSheet("QPushButton{background-color:#30a7b8;"
                                                  "border:none;"
#                                                  "color:#ffffff;"
                                                  "font-size:12px;"
                                                  "font-family:Tahoma;}"
                                      "QPushButton:hover{background-color:#ea5e00;}"
                                      "QPushButton:pressed{background-color:#994005;}")
        
        wdgt_page1=QtGui.QWidget(self)
        
        self.qbtn_cpy1=SVGPushButton("", wdgt_page1)
        self.qbtn_cpy1.addPixmap(ico_pixcpy.pixmap((QtCore.QSize(20,20))))
        self.qbtn_cpy1.setGeometry(250+85,135-34,22,22)
        #qbtn_cpy1.setFlat(True)
        self.qbtn_cpy1.setStyleSheet("QPushButton{border:none;}"
                                "QPushButton:hover{background-color:#51c0d1;}"
                                "QPushButton:pressed{background-color:#268392;}")

        self.qbtn_cpy2=SVGPushButton("", wdgt_page1)
        self.qbtn_cpy2.addPixmap(ico_pixcpy.pixmap((QtCore.QSize(20,20))))
        self.qbtn_cpy2.setGeometry(250+85,170-34,22,22)
        self.qbtn_cpy2.setStyleSheet("QPushButton{border:none;}"
                                "QPushButton:hover{background-color:#51c0d1;}"
                                "QPushButton:pressed{background-color:#268392;}")

        self.qbtn_cpy3=SVGPushButton("", wdgt_page1)
        self.qbtn_cpy3.addPixmap(ico_pixcpy.pixmap((QtCore.QSize(20,20))))
        self.qbtn_cpy3.setGeometry(250+85,205-34,22,22)
        self.qbtn_cpy3.setStyleSheet("QPushButton{border:none;}"
                                "QPushButton:hover{background-color:#51c0d1;}"
                                "QPushButton:pressed{background-color:#268392;}")
        
        qlbl_0 = QtGui.QLabel(u"Mapping file", wdgt_page1)
        qlbl_0.setGeometry(25,45-34,90,20)
        qlbl_0.setStyleSheet("QLabel{border:none;color:#2f2f2f;font-size:13px;font-family:Microsoft YaHei;}")
        
        
        qlbl_1 = QtGui.QLabel(u"Variable", wdgt_page1)
        qlbl_1.setGeometry(25,110-34,60,20)
        qlbl_1.setStyleSheet("QLabel{border:none;color:#2f2f2f;font-size:13px;font-family:Microsoft YaHei;}")
        
        qlbl_2 = QtGui.QLabel(u"Address", wdgt_page1)
        qlbl_2.setGeometry(250,110-34,60,20)
        qlbl_2.setStyleSheet("QLabel{border:none;color:#2f2f2f;font-size:13px;font-family:Microsoft YaHei;}")
        
        qlbl_3 = QtGui.QLabel(u"Bytes", wdgt_page1)
        qlbl_3.setGeometry(370,110-34,60,20)
        qlbl_3.setStyleSheet("QLabel{border:none;color:#2f2f2f;font-size:13px;font-family:Microsoft YaHei;}")
        
        qlbl_4 = QtGui.QLabel(u"Section", wdgt_page1)
        qlbl_4.setGeometry(420,110-34,120,20)
        qlbl_4.setStyleSheet("QLabel{border:none;color:#2f2f2f;font-size:13px;font-family:Microsoft YaHei;}")
        
        
        #self.qedt_filepath = QtGui.QLineEdit(input_file_path, self)
        self.qedt_filepath = EditDrop(input_file_path, wdgt_page1)
        self.qedt_filepath.setGeometry(25,70-34,433,22)
        self.qedt_filepath.setStyleSheet("QLineEdit{background-color:#e4e4e4;"
                                                    "border:none;"
                                                    "color:#2f2f2f;"
                                                    "font-size:12px;"
                                                    "font-family:Meiryo UI;}"
                                        "QLineEdit:hover{background-color:#e4e4e4;}")
        
        self.qbtn_filebrowser=QtGui.QPushButton(u"...", wdgt_page1)
        self.qbtn_filebrowser.setGeometry(458,70-34,22,22)
        self.qbtn_filebrowser.setStyleSheet("QPushButton{background-color:#30a7b8;"
                                                          "border:none;"
                                                          "color:#ffffff;"
                                                          "font-size:14px;"
                                                          "font-family:Meiryo UI;}"
                                            "QPushButton:hover{background-color:#51c0d1;}"
                                            "QPushButton:pressed{background-color:#268392;}")
        
        self.qbtn_fileload=QtGui.QPushButton(u"Load", wdgt_page1)
        self.qbtn_fileload.setGeometry(485,70-34,40,22)
        self.qbtn_fileload.setStyleSheet("QPushButton{background-color:#30a7b8;"
                                                          "border:none;"
                                                          "color:#ffffff;"
                                                          "font-size:13px;"
                                                          "font-family:Georgia;}"
                                            "QPushButton:hover{background-color:#51c0d1;}"
                                            "QPushButton:pressed{background-color:#268392;}")
        
        self.qedt_vari1 = QtGui.QLineEdit("", wdgt_page1)
        self.qedt_vari1.setGeometry(25,135-34,210,22)
        self.qedt_vari1.setStyleSheet("QLineEdit{background-color:#e4e4e4;border:none;color:#2f2f2f;font-size:12px;font-family:Meiryo UI;}QLineEdit:hover{background-color:#e4e4e4;}")
        
        self.qedt_vari2 = QtGui.QLineEdit("", wdgt_page1)
        self.qedt_vari2.setGeometry(25,170-34,210,22)
        self.qedt_vari2.setStyleSheet("QLineEdit{background-color:#e4e4e4;border:none;color:#2f2f2f;font-size:12px;font-family:Meiryo UI;}QLineEdit:hover{background-color:#e4e4e4;}")
        
        self.qedt_vari3 = QtGui.QLineEdit("", wdgt_page1)
        self.qedt_vari3.setGeometry(25,205-34,210,22)
        self.qedt_vari3.setStyleSheet("QLineEdit{background-color:#e4e4e4;border:none;color:#2f2f2f;font-size:12px;font-family:Meiryo UI;}QLineEdit:hover{background-color:#e4e4e4;}")
        
        
        self.qedt_addr1 = QtGui.QLineEdit("", wdgt_page1)
        self.qedt_addr1.setGeometry(250,135-34,85,22)
        self.qedt_addr1.setStyleSheet("QLineEdit{background-color:#e4e4e4;border:none;color:#2f2f2f;font-size:12px;font-family:Meiryo UI;}QLineEdit:hover{background-color:#e4e4e4;}")
        
        self.qedt_addr2 = QtGui.QLineEdit("", wdgt_page1)
        self.qedt_addr2.setGeometry(250,170-34,85,22)
        self.qedt_addr2.setStyleSheet("QLineEdit{background-color:#e4e4e4;border:none;color:#2f2f2f;font-size:12px;font-family:Meiryo UI;}QLineEdit:hover{background-color:#e4e4e4;}")
        
        self.qedt_addr3 = QtGui.QLineEdit("", wdgt_page1)
        self.qedt_addr3.setGeometry(250,205-34,85,22)
        self.qedt_addr3.setStyleSheet("QLineEdit{background-color:#e4e4e4;border:none;color:#2f2f2f;font-size:12px;font-family:Meiryo UI;}QLineEdit:hover{background-color:#e4e4e4;}")
        
#        qScrlArea=QtGui.QScrollArea(wdgt_page1)
#        qScrlArea.setGeometry(250+85,135-34,22,22)
#        #qScrlArea.setGeometry(10,0,64,64)
#        qsvg=QtSvg.QSvgWidget()
#        #qsvg.setGeometry(0,0,20,20)
#        ba_svg=QtCore.QByteArray(SVG_CPY2CLIPBOARD)
#        qsvg.renderer().load(ba_svg)
#        #qsvg.load(ba_svg)
#        qScrlArea.setWidget(qsvg)
        
        self.qedt_byte1 = QtGui.QLineEdit("", wdgt_page1)
        self.qedt_byte1.setGeometry(370,135-34,37,22)
        self.qedt_byte1.setAlignment(QtCore.Qt.AlignHCenter)
        self.qedt_byte1.setStyleSheet("QLineEdit{background-color:#e4e4e4;border:none;color:#2f2f2f;font-size:12px;font-family:Meiryo UI;}QLineEdit:hover{background-color:#e4e4e4;}")
        
        self.qedt_byte2 = QtGui.QLineEdit("", wdgt_page1)
        self.qedt_byte2.setGeometry(370,170-34,37,22)
        self.qedt_byte2.setAlignment(QtCore.Qt.AlignHCenter)
        self.qedt_byte2.setStyleSheet("QLineEdit{background-color:#e4e4e4;border:none;color:#2f2f2f;font-size:12px;font-family:Meiryo UI;}QLineEdit:hover{background-color:#e4e4e4;}")
        
        self.qedt_byte3 = QtGui.QLineEdit("", wdgt_page1)
        self.qedt_byte3.setGeometry(370,205-34,37,22)
        self.qedt_byte3.setAlignment(QtCore.Qt.AlignHCenter)
        self.qedt_byte3.setStyleSheet("QLineEdit{background-color:#e4e4e4;border:none;color:#2f2f2f;font-size:12px;font-family:Meiryo UI;}QLineEdit:hover{background-color:#e4e4e4;}")
        
        
        self.qedt_sect1 = QtGui.QLineEdit("", wdgt_page1)
        self.qedt_sect1.setGeometry(420,135-34,105,22)
        #self.qedt_sect1.setAlignment(QtCore.Qt.AlignRight)
        self.qedt_sect1.setStyleSheet("QLineEdit{background-color:#e4e4e4;border:none;color:#2f2f2f;font-size:12px;font-family:Meiryo UI;}QLineEdit:hover{background-color:#e4e4e4;}")
        
        self.qedt_sect2 = QtGui.QLineEdit("", wdgt_page1)
        self.qedt_sect2.setGeometry(420,170-34,105,22)
        self.qedt_sect2.setStyleSheet("QLineEdit{background-color:#e4e4e4;border:none;color:#2f2f2f;font-size:12px;font-family:Meiryo UI;}QLineEdit:hover{background-color:#e4e4e4;}")
        
        self.qedt_sect3 = QtGui.QLineEdit("", wdgt_page1)
        self.qedt_sect3.setGeometry(420,205-34,105,22)
        self.qedt_sect3.setStyleSheet("QLineEdit{background-color:#e4e4e4;border:none;color:#2f2f2f;font-size:12px;font-family:Meiryo UI;}QLineEdit:hover{background-color:#e4e4e4;}")
        
        qtab_main=QtGui.QTabWidget(self)
        qtab_main.setGeometry(0,34,552,210+34)
        qtab_main.setStyleSheet(
                                #"QWidget{background-color:#99d9ea;}"
                                "QTabWidget:pane{"
                                                #"background-color:#0f0f00;"
                                                #"font-size:12px;"
                                                "background-color:#99d9ea;"
                                                "border:none;"
                                                "}"
                                "QTabBar:tab{"
                                            #"font:bold;"
                                            "font-size:13px;"
                                            "font-family:Microsoft YaHei;"
                                            "color:#ffffff;"
                                            "height:28px;width:184px;"
                                            #"border-width:2px;"
                                            "}"
                                "QTabBar:tab:selected{background-color:#30a7b8;}"
                                "QTabBar:tab:!selected{background-color:#99d9ea;}"
                                "QTabBar:tab:!selected:hover{background-color:#50c0dc;}"
                                #"QTabBar:tab:hover{top: 2px;}"
                               )
        
        wdgt_page2=QtGui.QWidget(self)
        qlbl_2_0=QtGui.QLabel(u"Port", wdgt_page2)
        qlbl_2_0.setGeometry(25,45-34,90,20)
        qlbl_2_0.setStyleSheet("QLabel{border:none;color:#2f2f2f;font-size:13px;font-family:Microsoft YaHei;}")
        
        qlbl_2_1=QtGui.QLabel(u"Baud Rate", wdgt_page2)
        qlbl_2_1.setGeometry(25,75-34,90,20)
        qlbl_2_1.setStyleSheet("QLabel{border:none;color:#2f2f2f;font-size:13px;font-family:Microsoft YaHei;}")
        
        qlbl_2_2=QtGui.QLabel(u"Data Bits", wdgt_page2)
        qlbl_2_2.setGeometry(25,105-34,90,20)
        qlbl_2_2.setStyleSheet("QLabel{border:none;color:#2f2f2f;font-size:13px;font-family:Microsoft YaHei;}")
        
        qlbl_2_3=QtGui.QLabel(u"Parity", wdgt_page2)
        qlbl_2_3.setGeometry(25,135-34,90,20)
        qlbl_2_3.setStyleSheet("QLabel{border:none;color:#2f2f2f;font-size:13px;font-family:Microsoft YaHei;}")
        
        qlbl_2_4=QtGui.QLabel(u"Stop Bits", wdgt_page2)
        qlbl_2_4.setGeometry(25,165-34,90,20)
        qlbl_2_4.setStyleSheet("QLabel{border:none;color:#2f2f2f;font-size:13px;font-family:Microsoft YaHei;}")
        
        qcmb_2_0=QtGui.QComboBox(wdgt_page2)
        qcmb_2_0.setGeometry(115,45-34,90,20)
        qcmb_2_0.setStyleSheet("QComboBox{color:#2f2f2f;font-size:12px;font-family:Microsoft YaHei;}")
        qcmb_2_0.addItem("COM1")

        qcmb_2_1=QtGui.QComboBox(wdgt_page2)
        qcmb_2_1.setGeometry(115,75-34,90,20)
        qcmb_2_1.setStyleSheet("QComboBox{color:#2f2f2f;font-size:12px;font-family:Microsoft YaHei;}")

        qcmb_2_2=QtGui.QComboBox(wdgt_page2)
        qcmb_2_2.setGeometry(115,105-34,90,20)
        qcmb_2_2.setStyleSheet("QComboBox{color:#2f2f2f;font-size:12px;font-family:Microsoft YaHei;}")

        qcmb_2_3=QtGui.QComboBox(wdgt_page2)
        qcmb_2_3.setGeometry(115,135-34,90,20)
        qcmb_2_3.setStyleSheet("QComboBox{color:#2f2f2f;font-size:12px;font-family:Microsoft YaHei;}")

        qcmb_2_4=QtGui.QComboBox(wdgt_page2)
        qcmb_2_4.setGeometry(115,165-34,90,20)
        qcmb_2_4.setStyleSheet("QComboBox{color:#2f2f2f;font-size:12px;font-family:Microsoft YaHei;}")

        qbtn_EnumPorts=QtGui.QPushButton(u"EnumPorts", wdgt_page2)
        qbtn_EnumPorts.setGeometry(225,45-35,110,30)

        qbtn_OpenPort=QtGui.QPushButton(u"Open", wdgt_page2)
        qbtn_OpenPort.setGeometry(225,85-35,110,30)

        wdgt_page3=QtGui.QWidget(self)

        qtab_main.addTab(wdgt_page1, "Data Watch")
        qtab_main.addTab(wdgt_page2, "Setting")
        qtab_main.addTab(wdgt_page3, "About")

        # bind event
        self.qbtn_filebrowser.clicked.connect(self.btnClicked_filebrowser)
        self.qbtn_fileload.clicked.connect(self.btnClicked_fileload)
        self.qbtn_minimize.clicked.connect(self.btnClicked_minimize)
        self.qbtn_close.clicked.connect(self.btnClicked_close)
        self.qedt_vari1.textChanged.connect(self.edtTextChanged_vari1)
        self.qedt_vari2.textChanged.connect(self.edtTextChanged_vari2)
        self.qedt_vari3.textChanged.connect(self.edtTextChanged_vari3)
        self.qbtn_cpy1.clicked.connect(self.btnClicked_cpy1)
        self.qbtn_cpy2.clicked.connect(self.btnClicked_cpy2)
        self.qbtn_cpy3.clicked.connect(self.btnClicked_cpy3)
        qtab_main.currentChanged.connect(self.tabChanged_main)
        
        # init data
        self.lists = []

    # reload method to support window draging
    def mousePressEvent(self, event):
        if event.button()==Qt.LeftButton:
            self.m_drag=True
            self.m_DragPosition=event.globalPos()-self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if QMouseEvent.buttons() and Qt.LeftButton and self.m_drag:
            self.move(QMouseEvent.globalPos()-self.m_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag=False
    
    # event handle method
    def tabChanged_main(self, idx):
        pass
#        if idx == 2:
#            self.resize(800,500)

    def edtTextChanged_vari1(self, vari):
        for l in self.lists:
            if l[0] == vari:
                print vari
                self.qedt_addr1.setText(l[1])
                self.qedt_byte1.setText(l[2])
                self.qedt_sect1.setText(l[3])
                self.qedt_sect1.setCursorPosition(0)

    def edtTextChanged_vari2(self, vari):
        for l in self.lists:
            if l[0] == vari:
                self.qedt_addr2.setText(l[1])
                self.qedt_byte2.setText(l[2])
                self.qedt_sect2.setText(l[3])
                self.qedt_sect2.setCursorPosition(0)
                
    def edtTextChanged_vari3(self, vari):
        for l in self.lists:
            if l[0] == vari:
                self.qedt_addr3.setText(l[1])
                self.qedt_byte3.setText(l[2])
                self.qedt_sect3.setText(l[3])
                self.qedt_sect3.setCursorPosition(0)
                    
    def btnClicked_cpy1(self):
        QtGui.QApplication.clipboard().setText(self.qedt_addr1.text())
        QtGui.QToolTip.showText(self.mapToGlobal(self.qbtn_cpy1.pos())+QtCore.QPoint(25,41), "copyed")

    def btnClicked_cpy2(self):
        QtGui.QApplication.clipboard().setText(self.qedt_addr2.text())
        QtGui.QToolTip.showText(self.mapToGlobal(self.qbtn_cpy2.pos())+QtCore.QPoint(25,41), "copyed")

    def btnClicked_cpy3(self):
        QtGui.QApplication.clipboard().setText(self.qedt_addr3.text())
        QtGui.QToolTip.showText(self.mapToGlobal(self.qbtn_cpy3.pos())+QtCore.QPoint(25,41), "copyed")
        
    def btnClicked_filebrowser(self):
        map_filename = QtGui.QFileDialog.getOpenFileName(self, u"Select file", QtCore.QDir.currentPath(), "Map (*.map);;All files (*.*)")
        if map_filename:
            self.qedt_filepath.setText(map_filename)
        
    def btnClicked_fileload(self):
        map_filename = self.qedt_filepath.text().toLocal8Bit().data()
        #map_filename = r"D:\SVN_src\DenebMLK\ShootingStar\30_FW\32_Project\obj\ul8.map"
        succeed, map_lines = file_readlines(map_filename, 'rb')
        if succeed == False:
            print "Open map file failed."
            return
        
        RawData = [re_findVariables.search(l) for l in map_lines]
        self.lists = []
        
        for r in RawData:
            if r is not None:
                addr = int(r.group('addr'), 16)
                if addr > 0x7FFFFFFF:
                    addr -= 0x100000000
                self.lists.append([r.group('label'), "%d" % (addr), r.group('len'), r.group('section')])
        
        label_list = []
        for i in self.lists:
            label_list.append(i[0])
        
        qcmp_vari = QtGui.QCompleter(label_list)
        self.qedt_vari1.setCompleter(qcmp_vari)
        self.qedt_vari2.setCompleter(qcmp_vari)
        self.qedt_vari3.setCompleter(qcmp_vari)
        
        #QtGui.QToolTip.showText(self.qbtn_fileload.parentWidget().mapToGlobal(self.qbtn_fileload.pos())+QtCore.QPoint(-10,-44), "Loaded")
        QtGui.QToolTip.showText(self.mapToGlobal(self.qbtn_fileload.pos())+QtCore.QPoint(-10,-44), "Loaded")

    def btnClicked_minimize(self):
        self.showMinimized()

    def btnClicked_close(self):
        os._exit(0)

def file_readlines(path, mode):
    """read file's all lines to a lists"""
    try:
        f = open(path, mode)
    except IOError as e:
        print("{}".format(e).decode('string_escape'))
        QtGui.QMessageBox.warning(None, "I/O error({})".format(e.errno),
            "{0}: \'{1}\'".format(e.strerror, e.filename))
        return False, ""
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
        return False, ""
    else:
        string = f.readlines()
        f.close()
        return True, string

def file_write(path, string):
    """write string to a file"""
    try:
        f = open(path, 'w')
    except IOError as e:
        print("{}".format(e).decode('string_escape'))
        QtGui.QMessageBox.warning(None, "I/O error({})".format(e.errno),
            "{0}: \'{1}\'".format(e.strerror, e.filename))
        return False
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
        return False
    else:
        f.write(string)
        f.close()
        return True

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
    
if __name__=="__main__":
    mapp=QtGui.QApplication(sys.argv)
    mw=MainWindow(sys.argv)
    mw.show()
    sys.exit(mapp.exec_())


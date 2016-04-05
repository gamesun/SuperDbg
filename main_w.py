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
from PyQt4 import QtCore,QtGui
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
        
        self.resize(552,245)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        self.setStyleSheet("QWidget{background-color:#99d9ea;}")
        
        self.setWindowTitle(appInfo.title)
        
        self.scriptPath = os.path.dirname(os.path.realpath(argv[0]))
        input_file_path = (len(argv) > 1) and argv[1].decode("cp932") or u""
        
        zf = zipfile.ZipFile("%s/library.zip" % (self.scriptPath))
        pix16 = QtGui.QPixmap()
        pix16.loadFromData(zf.read("media/16.png"), "png")
        pix32 = QtGui.QPixmap()
        pix32.loadFromData(zf.read("media/32.png"), "png")
        
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
        qlbl_ico.setPixmap(pix32)
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
        qtab_main.setGeometry(0,34,552,210)
        qtab_main.setStyleSheet("QTabWidget:pane{border:none;"
                                                        #"color:#ffffff;"
                                                        #"font-size:12px;"
                                                        "}"
                                        #"QTabWidget:tab-bar{;}"
                                        "QTabBar:tab{border:none;"
                                                    "font:bold;"
                                                    "font-size:16px;"
                                                    "font-family:Georgia;"
                                                    "color:#ffffff;"
                                                    "height:28px;width:184px;"
                                                    "background-color:#30a7b8;}"
                                        "QTabBar:tab:selected{background-color:#30a7b8;alignment:center;}"
                                        "QTabBar:tab:!selected{background-color:#99d9ea;alignment:center;}"
                                        )
        
        wdgt_page2=QtGui.QWidget(self)
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

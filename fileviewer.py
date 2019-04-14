#!/usr/bin/env python

from PyQt5.QtCore import QDir, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (QWidget, QAction, QApplication, QFileDialog, QLabel,
        QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy, QSlider, QHBoxLayout, QGraphicsTransform)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
import photohs_reader
import QtImageViewer

class FileViewer(QMainWindow):
    layerChanged = pyqtSignal(int)
    filereader = None

    def __init__(self):
        super(FileViewer, self).__init__()

        self.scaleFactor = 0.0

        self.qWidget = QWidget()
        self.layerSlider = self.createSlider()
        self.layerSlider.setEnabled(False)

        self.layerSlider.valueChanged.connect(self.setLayer)
        self.layerChanged.connect(self.layerSlider.setValue)

        self.imageLabel = QtImageViewer.QtImageViewer()
        self.imageLabel.aspectRatioMode = Qt.KeepAspectRatioByExpanding
        self.imageLabel.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.imageLabel.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.imageLabel.canZoom = True
        self.imageLabel.canPan = True

        self.createActions()
        self.createMenus()
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.layerSlider)
        mainLayout.addWidget(self.imageLabel)

        self.qWidget.setLayout(mainLayout)
        self.setCentralWidget(self.qWidget)

        self.setWindowTitle("Photon S File Viewer")
        self.resize(600, 1050)

    def setLayer(self, layerNum):
        if layerNum == -1:
            image = self.filereader.get_preview_qtimage()            
        else:
            image = self.filereader.get_layer_qtimage(layerNum)
        self.imageLabel.setImage(QPixmap.fromImage(image))
        return
        

    def createSlider(self):
        slider = QSlider(Qt.Vertical)

        slider.setRange(0, 360)
        # slider.setSingleStep(16)
        slider.setPageStep(15)
        slider.setTickInterval(15)
        slider.setTickPosition(QSlider.TicksRight)

        return slider

    def open(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
                QDir.currentPath())
        if fileName:
            self.filereader = photohs_reader.PhotonSReader(fileName)
            self.filereader.read_data()
            image = self.filereader.get_layer_qtimage(0)
            if image.isNull():
                QMessageBox.information(self, "Photon S File Viewer",
                        "Cannot load %s." % fileName)
                return

            self.imageLabel.setImage(QPixmap.fromImage(image))

            self.layerSlider.setRange(-1, self.filereader.num_layers)
            self.layerSlider.setTickInterval(self.filereader.num_layers/15)
            self.layerSlider.setEnabled(True)
            self.scaleFactor = 1.0

            self.fitToWindowAct.setEnabled(True)

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.imageLabel.setWidgetResizable(fitToWindow)

    def about(self):
        QMessageBox.about(self, "About Photon S File Viewer",
                "<p>The <b>Photon S File Viewer</b> can parse and display "
                ".photons files. </p> ")

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False,
                checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)

        self.aboutAct = QAction("&About", self, triggered=self.about)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    imageViewer = FileViewer()
    imageViewer.show()
    sys.exit(app.exec_())

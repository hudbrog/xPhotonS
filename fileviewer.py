#!/usr/bin/env python

from PyQt5.QtCore import QDir, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import (QWidget, QAction, QApplication, QFileDialog, QLabel,
        QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy, QSlider, QHBoxLayout, QGraphicsTransform)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
import photons_reader
import photon_reader
import QtImageViewer
import ui

class FileViewer(QMainWindow):
    layerChanged = pyqtSignal(int)
    filereader = None
    ui = None

    def __init__(self):
        super(FileViewer, self).__init__()

        self.ui = ui.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.layerSlider.valueChanged.connect(self.setLayer)
        self.layerChanged.connect(self.ui.layerSlider.setValue)

        self.ui.actionOpen.triggered.connect(self.open)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionQuit.triggered.connect(self.close)

    def setLayer(self, layerNum):
        if layerNum == -1:
            image = self.filereader.get_preview_qtimage()            
        else:
            image = self.filereader.get_layer_qtimage(layerNum)
        self.ui.graphicsView.setImage(QPixmap.fromImage(image))
        return

    def populateModelInfo(self):
        self.ui.xyPixelSizeEdit.setText(str(self.filereader.getXYPixelSize()))
        self.ui.layerThicknessEdit.setText(str(self.filereader.getLayerThickness()))
        self.ui.normalExposureEdit.setText(str(self.filereader.getNormalExposureTime()))
        self.ui.bottomExposureEdit.setText(str(self.filereader.getBottomExposureTime()))
        self.ui.offTimeEdit.setText(str(self.filereader.getOffTime()))
        self.ui.bottomLayersEdit.setText(str(self.filereader.getNumBottomLayers()))
        self.ui.zLiftDistanceEdit.setText(str(self.filereader.getZLiftDistance()))
        self.ui.zLiftSpeedEdit.setText(str(self.filereader.getZLiftSpeed()))
        self.ui.zRetractSpeedEdit.setText(str(self.filereader.getZRetractSpeed()))
        self.ui.totalVolumeEdit.setText(str(self.filereader.getTotalVolume()))
        self.ui.numberLayersEdit.setText(str(self.filereader.getNumLayers()))
        self.ui.previewWEdit.setText(str(self.filereader.getPreviewW()))
        self.ui.previewHEdit.setText(str(self.filereader.getPreviewH()))

    def open(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
                QDir.currentPath())
        if fileName:
            if fileName.endswith(".photons"):
                self.filereader = photons_reader.PhotonSReader(fileName)
            elif fileName.endswith(".photon"):
                self.filereader = photon_reader.PhotonReader(fileName)
            self.filereader.read_data()
            image = self.filereader.get_layer_qtimage(0)
            # image = self.filereader.get_preview_qtimage()   
            if image.isNull():
                QMessageBox.information(self, "Photon S File Viewer",
                        "Cannot load %s." % fileName)
                return

            self.populateModelInfo()
            self.ui.graphicsView.setImage(QPixmap.fromImage(image))

            self.ui.layerSlider.setRange(-1, self.filereader.num_layers-1)
            self.ui.layerSlider.setTickInterval(self.filereader.num_layers/15)
            self.ui.layerSlider.setEnabled(True)

    def about(self):
        QMessageBox.about(self, "About Photon S File Viewer",
                "<p>The <b>Photon S File Viewer</b> can parse and display "
                ".photons files. </p> ")

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    imageViewer = FileViewer()
    imageViewer.show()
    sys.exit(app.exec_())

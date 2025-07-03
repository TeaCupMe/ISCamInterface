import sys
from qtdesigner.CM_Interface_UI import Ui_MainWindow
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QTime
from ISSerial import getPorts
from ISCamera import ISCamera
from serial import Serial
from time import time, sleep
import numpy as np
from PIL import Image, ImageQt
import os 

class CameraInterfaceApp(QtWidgets.QMainWindow, Ui_MainWindow):
    debugUI = False
    debugInterface = False
    ser:Serial    
    camera:ISCamera = ISCamera()
    def __init__(self, debugInterface = False, debugUI = False):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        self.debugUI = debugUI
        self.debugInterface = debugInterface
        
        
        super().__init__()
        
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'icon.png'))
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.getImageBar.setValue(0)
        self.clearLabels()
        self.updateComPortsList()
        self.updateSpeedsList()
        
        
    def clearLabels(self):
        self.exposureLabel.setText("")
        self.widthLabel.setText("")
        self.heightLabel.setText("")
        self.chunksLabel.setText("")
    def takePictureButtonPressed(self):
        # self.terminalTextBrowser.insertPlainText()
        self.displayDebugTextInTerminal("'Take Picture' pressed")
        self.takePicture()

    def getImageButtonPressed(self):
        self.displayDebugTextInTerminal("'Get Image' pressed")
        self.getImage()
        
    def getImagePropertiesButtonPressed(self):
        self.displayDebugTextInTerminal("'Get Image Properties' pressed")  
        self.getImageProperties()
        
    def setSizeButtonPressed(self):
        self.displayDebugTextInTerminal("'Set Size' pressed")
        self.setSize()

    def setExposureButtonPressed(self):
        value = self.exposureInput.text()
        self.displayDebugTextInTerminal(f"'Set Exposure' pressed with value {value}")
        self.setExposure()

            
    def displayDebugTextInTerminal(self, content:str, formatting = None):
        if self.debugUI:    
            self.terminalTextBrowser.insertPlainText("[DEBUG] " + content + "\n")
            self.terminalTextBrowser.verticalScrollBar().setValue(self.terminalTextBrowser.verticalScrollBar().maximum())
        
    def displayTextInTerminal(self, content:str):
        self.terminalTextBrowser.insertPlainText(content)
        self.terminalTextBrowser.verticalScrollBar().setValue(self.terminalTextBrowser.verticalScrollBar().maximum())
        
    def updateComPortsList(self):
        ports = getPorts()
        self.portSelectorComboBox.clear()
        self.portSelectorComboBox.addItems(ports)
    
    def updateSpeedsList(self):
        speeds = [
            "230400",
            "1000000"
        ]
        self.speedSelectorComboBox.clear()
        self.speedSelectorComboBox.addItems(speeds)
    
    def getImageProperties(self):
        with Serial(self.portSelectorComboBox.currentText(), int(self.speedSelectorComboBox.currentText()), timeout = 3) as serial:
            properties = self.camera.getProperties(serial)
            self.displayDebugTextInTerminal("Received image properties: " + str(properties))
            self.exposureLabel.setText(str(properties["exposure"]))
            self.chunksLabel.setText(str(properties["numberOfChunks"]))
            self.widthLabel.setText(str(properties["width"]))
            self.heightLabel.setText(str(properties["height"]))
        
    def getImage(self):
        # properties = self.camera.imageProperties
        # self.displayDebugTextInTerminal(str(properties))
        # self.scene = QtWidgets.QGraphicsScene(self)
        # self.imageView.setScene(self.scene)
        # self.pixmap_item = self.scene.addPixmap(QtGui.QPixmap())
        # # self.pixmap_item.setPixmap(QtGui.QPixmap("./icon.png"))
        # image = Image.new("L", (properties["width"], properties["height"])) # TODO - add color support
        # imageData = [255] * (properties["width"]*properties["height"])
        # raw = []
        # with open("rawdata.bin", "rb") as f:
        #     # raw = [i for i in f.read()[:properties["width"]*properties["height"]]]
        #     raw = [i for i in f.read()]
        # for chunkID in range(properties["numberOfChunks"]):
        #     for i in range(240):
        #         imageData[240*chunkID+i] = raw[chunkID*240 + i]
                
        #     image.putdata(imageData)
        #     self.pixmap_item.setPixmap(QtGui.QPixmap(ImageQt.toqpixmap(image)))
        #     sleep(0.001)
        #     QtWidgets.QApplication.instance().processEvents()
        #     # .processEvents()
            
            
        with Serial(self.portSelectorComboBox.currentText(), int(self.speedSelectorComboBox.currentText()), timeout = 3) as serial:
            imageProperties = self.camera.getProperties(serial)
            self.displayDebugTextInTerminal(str(imageProperties))
            numberOfChunks = imageProperties["numberOfChunks"]
            
            self.scene = QtWidgets.QGraphicsScene(self)
            self.imageView.setScene(self.scene)
            self.pixmap_item = self.scene.addPixmap(QtGui.QPixmap())
            
            image = Image.new("L", (imageProperties["width"], imageProperties["height"]))
            imageData = [0] * (imageProperties["width"]*imageProperties["height"])
            
            currentChunk = 0
            
            while (currentChunk<numberOfChunks-1):
                chunk = self.camera.getNextChunk(serial)
                self.displayDebugTextInTerminal(f"Chunk {chunk['chunkID']} received!")
                QtWidgets.QApplication.instance().processEvents() # type: ignore
                currentChunk = chunk["chunkID"]
                imgPart = chunk["payload"][:chunk["payloadLength"]]
                for i in range(chunk["payloadLength"]):
                    imageData[240*currentChunk+i] = imgPart[i]
                image.putdata(imageData)
                self.pixmap_item.setPixmap(QtGui.QPixmap(ImageQt.toqpixmap(image)))
                self.getImageBar.setValue(int(currentChunk*100/numberOfChunks))
                # QtWidgets.QApplication.instance().processEvents()
            self.getImageBar.setValue(100)
                 
            
    def takePicture(self):
        with Serial(self.portSelectorComboBox.currentText(), int(self.speedSelectorComboBox.currentText()), timeout = 3) as serial:
            t = time()
            self.camera.takeImage(serial)
            self.displayTextInTerminal(f"Image taken in {(time() - t):.3f} seconds")
    
    def setExposure(self):
        with Serial(self.portSelectorComboBox.currentText(), int(self.speedSelectorComboBox.currentText()), timeout = 3) as serial:
            value:str = self.exposureInput.text()
            if not value.isdigit():
                self.displayTextInTerminal("Введите желаемое значение экспозиции!\n")
                return
            intValue = int(value)
            if intValue>509:
                self.displayTextInTerminal("Значение экспозиции не может быть больше 509!\n")
            self.camera.setExposure(intValue, serial)
    
    def setSize(self):
        with Serial(self.portSelectorComboBox.currentText(), int(self.speedSelectorComboBox.currentText()), timeout = 3) as serial:         
            width:str = self.widthInput.text()
            height:str = self.heightInput.text()
            
            if not (width.isdigit() and height.isdigit()):
                self.displayTextInTerminal("Введите значения ширины и высоты!\n")
                return
            intWidth = int(width)
            intHeight = int(height)
            if intHeight <= 0 or intHeight > 480:
                self.displayTextInTerminal("Высота должна быть в диапазоне 1-480\n")
                return
            if intWidth <= 0 or intWidth > 640:
                self.displayTextInTerminal("Ширина должна быть в диапазоне 1-640\n")
                return
            
            self.camera.setSize(intWidth, intHeight, serial)
        
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = CameraInterfaceApp(False, True)  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec()  # и запускаем приложение
    
    
if __name__ == "__main__":
    main()
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtSerialPort

from asm5_gui import Ui_MainWindow
from asm5_mpl import ASMPlotCanvasStatic
from asm5_mpl import ASMPlotCanvasDynamic

import sys
import serial
import serial.tools.list_ports

_translate = QtCore.QCoreApplication.translate

# ASM Variables and functions --------------------------------------------------
ProgramName = "Arduino Serial Monitor"

ASMSensorList = [
    "Select sensor",
    "Accelerometer",
    "Barometer",
    "Termohigrometer",
    "Ultasonic Rangin Module"
]


def ASMScanSerialPorts():
    availablePorts = serial.tools.list_ports.comports()
    enabledPorts = [port for port in availablePorts if port[2] != 'n/a']
    return enabledPorts


def ASMSerialPortsNameList():
    enabledPorts = ASMScanSerialPorts()
    enabledPortsNames = [port[1] for port in enabledPorts]
    return enabledPortsNames


# ASM GUI object and functions -------------------------------------------------
class ASM(QtWidgets.QMainWindow):

    def __init__(self):
        super(ASM, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.SELSensor.currentIndexChanged.connect(self.SELSensorOnCurrentIndexChanged)
        self.ui.SELBaudRate.currentIndexChanged.connect(self.SELBaudRateOnCurrentIndexChanged)
        self.ui.SELSerialPort.currentIndexChanged.connect(self.SELSerialPortOnCurrentIndexChanged)
        self.ui.BTNOpenPort.clicked.connect(self.BTNOpenPortOnClick)
        self.ui.BTNClosePort.clicked.connect(self.BTNClosePortOnClick)

        self.ui.PlotLayout.addWidget(ASMPlotCanvasDynamic(self.ui.DisplayPanel, width=5, height=4, dpi=100))
        # self.ui.INDelay.clicked.connect(self.Dummy)
        # self.ui.BTNSetDelay.clicked.connect(self.Dummy)

        # self.SerialPort = QtSerialPort.QSerialPort()
        # self.SerialPortInfo = None

        """
            SELSensor
            SELBaudRate
            SELSerialPort
            BTNOpenPort
            BTNClosePort
            INDelay
            BTNSetDelay
            LBLBaudRate
            LBLDelay
            LBLMagnitude1
            LBLMagnitude2
            LBLMagnitude3
            LBLSensorType
            LBLSerialPort
            LBLTime
            LCDMagnitude1
            LCDMagnitude2
            LCDMagnitude3
            LDCTime
            PlotLayout
        """
        # propertyList = dir(self.ui.BTNOpenPort)
        # propertyList = dir(self.ui.SELSensor)
        # propertyList.sort()
        # for i in propertyList:
        #     print(i)
        # print()
        self.show()

    def Dummy(self):
        print("holi")

    def _ScanSerialPorts(self):
        AvailableSerialPorts = QtSerialPort.QSerialPortInfo.availablePorts()
        AvailableSerialPortsNames = ["{0:} ({1:})".format(port.portName(), port.manufacturer()) if port.manufacturer() != 0 else "{0:}".format(port.portName()) for port in AvailableSerialPorts]

        return AvailableSerialPortsNames

    def _updateSELSerialPortItems(self):
        AvailableSerialPortsNames = self._ScanSerialPorts()

        self.ui.SELSerialPort.setItemText(0, _translate("MainWindow", "Select port"))

        if len(AvailableSerialPortsNames) == 0:
            self.ui.SELSerialPort.setItemText(0, _translate("MainWindow", "Serial ports not found"))

        else:
            for i in range(1, self.ui.SELSerialPort.count() + 1):
                self.ui.SELSerialPort.removeItem(i)
            self.ui.SELSerialPort.addItems(AvailableSerialPortsNames)

    def _EnableSELSensor(self):
        if self.ui.BTNClosePort.isEnabled():
            self.ui.SELSensor.setEnabled(False)
        else:
            self.ui.SELSensor.setEnabled(True)

    def _EnableSELSerialPort(self):
        conditions = [
            self.ui.SELSensor.isEnabled(),
            self.ui.SELSensor.currentIndex() != 0,
        ]

        if all(conditions):
            self._updateSELSerialPortItems()
            self.ui.SELSerialPort.setEnabled(True)
        else:
            self.ui.SELSerialPort.setEnabled(False)
            self.ui.SELSerialPort.setCurrentIndex(0)

    def _EnableSELBaudRate(self):
        conditions = [
            self.ui.SELSensor.isEnabled(),
            self.ui.SELSensor.currentIndex() != 0,
            self.ui.SELSerialPort.isEnabled(),
            self.ui.SELSerialPort.currentIndex() != 0,
        ]

        if all(conditions):
            self.ui.SELBaudRate.setEnabled(True)
        else:
            self.ui.SELBaudRate.setEnabled(False)
            self.ui.SELBaudRate.setCurrentIndex(0)

    def _EnableBTNOpenPort(self):
        conditions = [
            self.ui.SELSensor.isEnabled(),
            self.ui.SELSensor.currentIndex() != 0,
            self.ui.SELSerialPort.isEnabled(),
            self.ui.SELSerialPort.currentIndex() != 0,
            self.ui.SELBaudRate.isEnabled(),
            self.ui.SELBaudRate.currentIndex() != 0,
        ]

        if all(conditions):
            self.ui.BTNOpenPort.setEnabled(True)
        else:
            self.ui.BTNOpenPort.setEnabled(False)

    def _EnableBTNClosePort(self):
        # BTNOpenPort
        pass

    def _EnableINDelay(self):
        conditions = [
            self.ui.BTNClosePort.isEnabled(),
        ]

        if all(conditions):
            self.ui.INDelay.setEnabled(True)
        else:
            self.ui.INDelay.setEnabled(False)

    def _EnableBTNSetDelay(self):
        conditions = [
            self.ui.BTNClosePort.isEnabled(),
        ]

        if all(conditions):
            self.ui.BTNSetDelay.setEnabled(True)
        else:
            self.ui.BTNSetDelay.setEnabled(False)

    def OpenSerialPort(self):
        SerialPortName = self.ui.SELSerialPort.itemText(self.ui.SELSerialPort.currentIndex())
        SerialPortBaudRate = int(self.ui.SELBaudRate.itemText(self.ui.SELBaudRate.currentIndex())[0:-5])
        self.SerialPort.setPortName(SerialPortName)
        self.SerialPort.setBaudRate(SerialPortBaudRate)
        self.SerialPortInfo = QtSerialPort.QSerialPortInfo(self.SerialPort)

        if not self.SerialPortInfo.isBusy():
            self.SerialPort.open(QtSerialPort.QSerialPort.ReadWrite)
            if self.SerialPort.isOpen():
                print("Open weona x)")
            else:
                print("Not open :(")

        print("Port: {0:}".format(self.SerialPortInfo.portName()))
        print("Location: {0:}".format(self.SerialPortInfo.systemLocation()))
        print("Description: {0:}".format(self.SerialPortInfo.description()))
        print("Manufacturer: {0:}".format(self.SerialPortInfo.manufacturer()))
        print("Serial number: {0:}".format(self.SerialPortInfo.serialNumber()))
        print("Vendor Identifier: {0:}".format(self.SerialPortInfo.vendorIdentifier()))
        print("Product Identifier: {0:}".format(self.SerialPortInfo.productIdentifier()))
        print("Busy: {0:}".format(self.SerialPortInfo.isBusy()))

    def SELSensorOnCurrentIndexChanged(self):
        self._EnableSELBaudRate()
        self._EnableSELSerialPort()
        self._EnableBTNClosePort()
        self._EnableBTNOpenPort()
        self._EnableINDelay()
        self._EnableBTNSetDelay()

    def SELSerialPortOnCurrentIndexChanged(self):
        self._EnableSELBaudRate()
        self._EnableBTNClosePort()
        self._EnableBTNOpenPort()
        self._EnableINDelay()
        self._EnableBTNSetDelay()

    def SELBaudRateOnCurrentIndexChanged(self):
        self._EnableBTNClosePort()
        self._EnableBTNOpenPort()
        self._EnableINDelay()
        self._EnableBTNSetDelay()

    def BTNOpenPortOnClick(self):
        # self.OpenSerialPort()
        self.ui.SELSensor.setEnabled(False)
        self.ui.SELBaudRate.setEnabled(False)
        self.ui.SELSerialPort.setEnabled(False)
        self.ui.BTNOpenPort.setEnabled(False)
        self.ui.BTNClosePort.setEnabled(True)
        self._EnableINDelay()
        self._EnableBTNSetDelay()

    def BTNClosePortOnClick(self):
        self.ui.SELSensor.setEnabled(True)
        self.ui.SELBaudRate.setEnabled(True)
        self.ui.SELSerialPort.setEnabled(True)
        self.ui.BTNOpenPort.setEnabled(True)
        self.ui.BTNClosePort.setEnabled(False)
        self._EnableINDelay()
        self._EnableBTNSetDelay()

    """
    def SELSensor(self):
        # SELSensor
        pass

    def SELBaudRate(self):
        # SELBaudRate
        pass

    def SELSerialPort(self):
        # SELSerialPort
        pass

    def BTNClosePort(self):
        # BTNClosePort
        pass

    def BTNOpenPort(self):
        # BTNOpenPort
        pass

    def INDelay(self):
        # INDelay
        pass

    def BTNSetDelay(self):
        # BTNSetDelay
        pass
    """


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = ASM()
    ex.setWindowTitle("{0:}".format(ProgramName))
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

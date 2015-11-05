from PyQt4 import QtGui

from asm_gui import Ui_MainWindow

import sys
import serial
import serial.tools.list_ports

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
class ASM(QtGui.QMainWindow):

    def __init__(self):
        super(ASM, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        """
            BTNClosePort
            BTNOpenPort
            BTNSetDelay
            INDelay
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
            SELBaudRate
            SELSensor
            SELSerialPort
            PlotLayout
        """

        self.SetSELSensorEnabled()
        self.SetSELBaudRateEnabled()
        self.SetSELSerialPortEnabled()
        self.ui.SELSerialPort.addItems(ASMSerialPortsNameList())
        self.show()

    @property
    def isSELSensorUsable(self):
        return self.ui.SELSensor.currentIndex() != 0

    @property
    def isSELBaudRateUsable(self):
        return self.ui.SELBaudRate.currentIndex() != 0

    @property
    def isSELSerialPortUsable(self):
        return self.ui.SELSerialPort.currentIndex() != 0

    def SetSELSensorEnabled(self):
        self.ui.SELSensor.setEnabled(True)

    def SetSELBaudRateEnabled(self):
        self.ui.SELBaudRate.setEnabled(self.isSELSensorUsable)

    def SetSELSerialPortEnabled(self):
        self.ui.SELSerialPort.setEnabled(self.isSELSensorUsable and self.isSELBaudRateUsable)


def main():
    app = QtGui.QApplication(sys.argv)
    ex = ASM()
    ex.setWindowTitle("{0:}".format(ProgramName))
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

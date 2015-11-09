from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtSerialPort

from asm5_gui import Ui_MainWindow
from asm5_mpl import ASMPlotCanvas
from asm5_mpl import ASMAccelerometerPlot
from asm5_mpl import ASMBarometerPlot
from asm5_mpl import ASMThermohygrometer
from asm5_mpl import ASMUltrasonicPlot
from asm5_mpl import ASMUVRadiationPlot

import datetime
import sys

_translate = QtCore.QCoreApplication.translate

# ASM Variables and functions --------------------------------------------------
ProgramName = "Arduino Serial Monitor"

ACE = "Accelerometer"
BAR = "Barometer"
THE = "Thermohygrometer"
ULT = "Ultasonic Rangin Module"
UVR = "UV Radiation Sensor"

ASMSensorList = [
    ACE,
    BAR,
    THE,
    ULT,
    UVR,
]

ASMSensorDataKeys = {
    ACE: ["X", "Y", "Z"],
    BAR: ["S", "T", "P"],
    THE: ["S", "T", "H", "W"],
    ULT: ["D"],
    UVR: ["U"],
}

ASMSensorMagnitudeMap = {
    "t": {
        "Name": "Time",
        "Label": "Time (s)",
    },
    "X": {
        "Name": "X angle",
        "Label": "X angle (deg)",
    },
    "Y": {
        "Name": "Y angle",
        "Label": "Y angle (deg)",
    },
    "Z": {
        "Name": "Z angle",
        "Label": "Z angle (deg)",
    },
    "S": {
        "Name": "Status",
        "Label": "Status",
    },
    "T": {
        "Name": "Temperature",
        "Label": "Temperature (°C)",
    },
    "P": {
        "Name": "Pressure",
        "Label": "Pressure (mmHg)",
    },
    "H": {
        "Name": "Humidity",
        "Label": "Humidity (%)",
    },
    "D": {
        "Name": "Distance",
        "Label": "Distance (cm)",
    },
    "W": {
        "Name": "Dew Point",
        "Label": "Dew Point (°C)",
    },
    "U": {
        "Name": "UV Intensity",
        "Label": "UV Intensity (mW/cm^2)",
    },
    "-": {
        "Name": "None",
        "Label": "None",
    },
}

ASMGoodStatus = 0
ASMBadData = -999.0


# ASM GUI object and functions -------------------------------------------------
class ASM(QtWidgets.QMainWindow):

    def __init__(self):
        super(ASM, self).__init__()

        self.SerialPort = None
        self.SerialPortInfo = None
        self.Time = 0
        self.Data = {}

        self.UserInterface = Ui_MainWindow()
        self.UserInterface.setupUi(self)

        for sensorName in ASMSensorList:
            self.UserInterface.SELSensor.addItem(_translate("MainWindow", sensorName))

        self.UserInterface.SELSensor.currentIndexChanged.connect(self.SELSensorOnCurrentIndexChanged)
        self.UserInterface.SELBaudRate.currentIndexChanged.connect(self.SELBaudRateOnCurrentIndexChanged)
        self.UserInterface.SELSerialPort.currentIndexChanged.connect(self.SELSerialPortOnCurrentIndexChanged)
        self.UserInterface.BTNOpenPort.clicked.connect(self.BTNOpenPortOnClick)
        self.UserInterface.BTNClosePort.clicked.connect(self.BTNClosePortOnClick)

        self.PlotCanvas = ASMPlotCanvas(self.UserInterface.DisplayPanel, width=5, height=4, dpi=100)
        self.UserInterface.PlotLayout.addWidget(self.PlotCanvas)

        # self.UserInterface.INDelay.clicked.connect(self.Dummy)
        self.UserInterface.BTNSetDelay.clicked.connect(self.BTNSetDelayOnClick)

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

        # properties = dir(self.UserInterface.INDelay)
        # for property in properties:
        #     if '_' not in property:
        #         print(property)
        #         pass
        self.show()

    def _ScanSerialPorts(self):
        AvailableSerialPorts = QtSerialPort.QSerialPortInfo.availablePorts()
        AvailableSerialPortsNames = ["{0:} ({1:})".format(port.portName(), port.manufacturer()) if port.manufacturer() != 0 else "{0:}".format(port.portName()) for port in AvailableSerialPorts]

        return AvailableSerialPortsNames

    def _updateSELSerialPortItems(self):
        AvailableSerialPortsNames = self._ScanSerialPorts()

        self.UserInterface.SELSerialPort.setItemText(0, _translate("MainWindow", "Select port"))

        if len(AvailableSerialPortsNames) == 0:
            self.UserInterface.SELSerialPort.setItemText(0, _translate("MainWindow", "Serial ports not found"))

        else:
            for i in range(1, self.UserInterface.SELSerialPort.count() + 1):
                self.UserInterface.SELSerialPort.removeItem(i)
            self.UserInterface.SELSerialPort.addItems(AvailableSerialPortsNames)

    def _EnableSELSensor(self):
        if self.UserInterface.BTNClosePort.isEnabled():
            self.UserInterface.SELSensor.setEnabled(False)
        else:
            self.UserInterface.SELSensor.setEnabled(True)

    def _EnableSELSerialPort(self):
        conditions = [
            self.UserInterface.SELSensor.isEnabled(),
            self.UserInterface.SELSensor.currentIndex() != 0,
        ]

        if all(conditions):
            self._updateSELSerialPortItems()
            self.UserInterface.SELSerialPort.setEnabled(True)
        else:
            self.UserInterface.SELSerialPort.setEnabled(False)
            self.UserInterface.SELSerialPort.setCurrentIndex(0)

    def _EnableSELBaudRate(self):
        conditions = [
            self.UserInterface.SELSensor.isEnabled(),
            self.UserInterface.SELSensor.currentIndex() != 0,
            self.UserInterface.SELSerialPort.isEnabled(),
            self.UserInterface.SELSerialPort.currentIndex() != 0,
        ]

        if all(conditions):
            self.UserInterface.SELBaudRate.setEnabled(True)
        else:
            self.UserInterface.SELBaudRate.setEnabled(False)
            self.UserInterface.SELBaudRate.setCurrentIndex(0)

    def _EnableBTNOpenPort(self):
        conditions = [
            self.UserInterface.SELSensor.isEnabled(),
            self.UserInterface.SELSensor.currentIndex() != 0,
            self.UserInterface.SELSerialPort.isEnabled(),
            self.UserInterface.SELSerialPort.currentIndex() != 0,
            self.UserInterface.SELBaudRate.isEnabled(),
            self.UserInterface.SELBaudRate.currentIndex() != 0,
        ]

        if all(conditions):
            self.UserInterface.BTNOpenPort.setEnabled(True)
        else:
            self.UserInterface.BTNOpenPort.setEnabled(False)

    def _EnableBTNClosePort(self):
        conditions = [
            not self.UserInterface.SELSensor.isEnabled()
        ]

        if all(conditions):
            self.UserInterface.BTNClosePort.setEnabled(True)
        else:
            self.UserInterface.BTNClosePort.setEnabled(False)

    def _EnableINDelay(self):
        conditions = [
            self.UserInterface.BTNClosePort.isEnabled(),
        ]

        if all(conditions):
            self.UserInterface.INDelay.setEnabled(True)
        else:
            self.UserInterface.INDelay.setEnabled(False)

    def _EnableBTNSetDelay(self):
        conditions = [
            self.UserInterface.BTNClosePort.isEnabled(),
        ]

        if all(conditions):
            self.UserInterface.BTNSetDelay.setEnabled(True)
        else:
            self.UserInterface.BTNSetDelay.setEnabled(False)

    def _OpenSerialPort(self):
        SerialPortName = self.UserInterface.SELSerialPort.itemText(self.UserInterface.SELSerialPort.currentIndex()).split(" ")[0]
        SerialPortBaudRate = int(self.UserInterface.SELBaudRate.itemText(self.UserInterface.SELBaudRate.currentIndex())[0:-5])

        self.SerialPort = QtSerialPort.QSerialPort()

        self.SerialPort.setPortName(SerialPortName)
        self.SerialPort.setBaudRate(SerialPortBaudRate)

        self.SerialPortInfo = QtSerialPort.QSerialPortInfo(self.SerialPort)

        if not self.SerialPortInfo.isBusy():
            try:
                self.SerialPort.open(QtSerialPort.QSerialPort.ReadWrite)
                self.SerialPort.readyRead.connect(self._SerialPortProcessor)
                return True

            except:
                # Launch QTMessageBox
                pass
        else:
            # Launch QTMessageBox
            pass

        return False

    def _CloseSerialPort(self):
        try:
            self.SerialPort.close()
            return True
        except:
            # Launch QTMessageBox
            pass

        return False

    def _SerialPortProcessor(self):
            if self.SerialPort.canReadLine():
                try:
                    text = self.SerialPort.readLine()
                    text = bytes(text).decode('utf-8').replace('\r', '').replace('\n', '')
                    self.Data = text.split('|')
                    self.Data = dict([item.split(':') for item in self.Data])

                    if 'M' in list(self.Data.keys()):
                        self.UserInterface.SerialConsole.append(" * Change delay to: {0:} ms".format(self.Data['M']))
                    else:
                        if self._DataFormatVerification():
                            self.UserInterface.SerialConsole.append(" * {0:}".format(self.Data))
                            self._UpdatePlotter()

                except:
                    # launch QtMessageBox
                    pass

    def _DataFormatVerification(self):
        sensor = self.UserInterface.SELSensor.currentText()

        try:
            InCommingsensorKeys = list(self.Data.keys())
            NativeCommingsensorKeys = ASMSensorDataKeys[sensor]
            InCommingsensorKeys.sort()
            NativeCommingsensorKeys.sort()

            if InCommingsensorKeys == NativeCommingsensorKeys:
                for k, v in self.Data.items():
                    self.Data[k] = round(float(v))

                if self.Time == 0:
                    self.Time = datetime.datetime.now()
                self.Data['t'] = round((datetime.datetime.now() - self.Time).total_seconds(), 2)

                if sensor == ACE:
                    self.UserInterface.LBLMagnitude1.setProperty("value", self.Data["X"])
                    self.UserInterface.LBLMagnitude2.setProperty("value", self.Data["Z"])
                    self.UserInterface.LBLMagnitude3.setProperty("value", self.Data["Y"])

                if sensor == BAR:
                    self.UserInterface.LCDMagnitude1.setProperty("value", self.Data["T"])
                    self.UserInterface.LCDMagnitude2.setProperty("value", self.Data["P"])

                if sensor == THE:
                    self.UserInterface.LCDMagnitude1.setProperty("value", self.Data["T"])
                    self.UserInterface.LCDMagnitude2.setProperty("value", self.Data["H"])
                    self.UserInterface.LCDMagnitude3.setProperty("value", self.Data["W"])

                if sensor == ULT:
                    self.UserInterface.LCDMagnitude1.setProperty("value", self.Data["D"])

                if sensor == UVR:
                    self.UserInterface.LCDMagnitude1.setProperty("value", self.Data["U"])

                self.UserInterface.LDCTime.setProperty("value", self.Data["t"])

                return True
        except:
            pass

        return False

    def _SetupPlotter(self):
        sensor = self.UserInterface.SELSensor.currentText()

        self.UserInterface.PlotLayout.removeWidget(self.PlotCanvas)
        del(self.PlotCanvas)
        if sensor == ACE:
            self.PlotCanvas = ASMAccelerometerPlot(self.UserInterface.DisplayPanel, width=5, height=4, dpi=100)
            self.UserInterface.LBLMagnitude1.setText(_translate("MainWindow", ASMSensorMagnitudeMap["X"]["Name"]))
            self.UserInterface.LBLMagnitude2.setText(_translate("MainWindow", ASMSensorMagnitudeMap["Z"]["Name"]))
            self.UserInterface.LBLMagnitude3.setText(_translate("MainWindow", ASMSensorMagnitudeMap["Y"]["Name"]))

        if sensor == BAR:
            self.PlotCanvas = ASMBarometerPlot(self.UserInterface.DisplayPanel, width=5, height=4, dpi=100)
            self.UserInterface.LBLMagnitude1.setText(_translate("MainWindow", ASMSensorMagnitudeMap["T"]["Name"]))
            self.UserInterface.LBLMagnitude2.setText(_translate("MainWindow", ASMSensorMagnitudeMap["P"]["Name"]))
            self.UserInterface.LBLMagnitude3.setText(_translate("MainWindow", ASMSensorMagnitudeMap["-"]["Name"]))

        if sensor == THE:
            self.PlotCanvas = ASMThermohygrometer(self.UserInterface.DisplayPanel, width=5, height=4, dpi=100)
            self.UserInterface.LBLMagnitude1.setText(_translate("MainWindow", ASMSensorMagnitudeMap["T"]["Name"]))
            self.UserInterface.LBLMagnitude2.setText(_translate("MainWindow", ASMSensorMagnitudeMap["H"]["Name"]))
            self.UserInterface.LBLMagnitude3.setText(_translate("MainWindow", ASMSensorMagnitudeMap["W"]["Name"]))

        if sensor == ULT:
            self.PlotCanvas = ASMUltrasonicPlot(self.UserInterface.DisplayPanel, width=5, height=4, dpi=100)
            self.UserInterface.LBLMagnitude1.setText(_translate("MainWindow", ASMSensorMagnitudeMap["D"]["Name"]))
            self.UserInterface.LBLMagnitude2.setText(_translate("MainWindow", ASMSensorMagnitudeMap["-"]["Name"]))
            self.UserInterface.LBLMagnitude3.setText(_translate("MainWindow", ASMSensorMagnitudeMap["-"]["Name"]))

        if sensor == UVR:
            self.PlotCanvas = ASMUVRadiationPlot(self.UserInterface.DisplayPanel, width=5, height=4, dpi=100)
            self.UserInterface.LBLMagnitude1.setText(_translate("MainWindow", ASMSensorMagnitudeMap["U"]["Name"]))
            self.UserInterface.LBLMagnitude2.setText(_translate("MainWindow", ASMSensorMagnitudeMap["-"]["Name"]))
            self.UserInterface.LBLMagnitude3.setText(_translate("MainWindow", ASMSensorMagnitudeMap["-"]["Name"]))

        self.UserInterface.LBLTime.setText(_translate("MainWindow", ASMSensorMagnitudeMap["t"]["Name"]))
        self.UserInterface.PlotLayout.addWidget(self.PlotCanvas)

    def _UpdatePlotter(self):
        try:
            self.PlotCanvas.addData(self.Data)
        except Exception as e:
            raise(e)
        # self.UserInterface.DisplayPanel.findChild(type(self.PlotCanvas)).addData(self.Data)
        # self.UserInterface.PlotLayout.replaceWidget(self.PlotCanvas)

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
            if self._OpenSerialPort():
                self.UserInterface.SELSensor.setEnabled(False)
                self.UserInterface.SELBaudRate.setEnabled(False)
                self.UserInterface.SELSerialPort.setEnabled(False)
                self.UserInterface.BTNOpenPort.setEnabled(False)

                self._EnableBTNClosePort()
                self._EnableINDelay()
                self._EnableBTNSetDelay()
                self._SetupPlotter()

                self.UserInterface.SerialConsole.setText("")
                self.UserInterface.SerialConsole.append("Configuration Summary: ")
                self.UserInterface.SerialConsole.append("* Sensor   : " + self.UserInterface.SELSensor.currentText())
                self.UserInterface.SerialConsole.append("* Port     : " + self.UserInterface.SELSerialPort.currentText())
                self.UserInterface.SerialConsole.append("* Baud Rate: " + self.UserInterface.SELBaudRate.currentText())
                self.UserInterface.SerialConsole.append("Collected data: ")

    def BTNClosePortOnClick(self):
        if self._CloseSerialPort():
            self.UserInterface.SELSensor.setEnabled(True)
            self.UserInterface.SELBaudRate.setEnabled(True)
            self.UserInterface.SELSerialPort.setEnabled(True)
            self.UserInterface.BTNOpenPort.setEnabled(True)

            self._EnableBTNClosePort()
            self._EnableINDelay()
            self._EnableBTNSetDelay()

            self.UserInterface.LBLMagnitude1.setText(_translate("MainWindow", "Magnitude 1"))
            self.UserInterface.LBLMagnitude2.setText(_translate("MainWindow", "Magnitude 2"))
            self.UserInterface.LBLMagnitude3.setText(_translate("MainWindow", "Magnitude 3"))
            self.UserInterface.LBLTime.setText(_translate("MainWindow", "Time"))

            self.UserInterface.LCDMagnitude1.setProperty("value", 0)
            self.UserInterface.LCDMagnitude2.setProperty("value", 0)
            self.UserInterface.LCDMagnitude3.setProperty("value", 0)
            self.UserInterface.LDCTime.setProperty("value", 0)

            self.UserInterface.PlotLayout.removeWidget(self.PlotCanvas)
            del(self.PlotCanvas)
            self.PlotCanvas = ASMPlotCanvas(self.UserInterface.DisplayPanel, width=5, height=4, dpi=100)
            self.UserInterface.PlotLayout.addWidget(self.PlotCanvas)
            self.Time = 0
            self.UserInterface.SerialConsole.setText("")

    def BTNSetDelayOnClick(self):
        try:
            Delay = int(self.UserInterface.INDelay.text())
            Delay = str(Delay).encode('utf-8')
            # Delay = bytes("{0:.0f}".format(Delay)+"\n")
            self.SerialPort.write(Delay)
        except Exception as e:
            print(e)
            pass
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = ASM()
    ex.setWindowTitle("{0:}".format(ProgramName))
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

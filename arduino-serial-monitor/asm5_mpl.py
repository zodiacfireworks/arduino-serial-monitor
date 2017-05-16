from PyQt5 import QtWidgets

import random
import matplotlib

matplotlib.use('Qt5Agg')

from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties

FontConfig = FontProperties(
    family="Roboto",
    style="normal",
    variant="normal",
    size=8
)

pyplot.rcParams['font.family'] = "Roboto"
pyplot.rcParams['font.size'] = 8


class ASMPlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.Figure = Figure(figsize=(width, height), dpi=dpi)
        self.Figure.set_facecolor('#FFFFFF')

        self.AxesLength = None
        self.Axes = {}

        FigureCanvas.__init__(self, self.Figure)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.initialConfiguration()

    def initialConfiguration(self):
        pass

    def addData(self, Data):
        try:
            for key in Data.keys():
                if key != 't' and key != 'S':
                    if self.Lines[key] is None:
                        self.Lines[key], = self.Axes[key].plot(Data['t'], Data[key], self.magnitudeMap[key]["Color"], label=self.magnitudeMap[key]["Label"])
                    else:
                        xData = list(self.Lines[key].get_xdata())
                        xData += [Data['t']]
                        yData = list(self.Lines[key].get_ydata())
                        yData += [Data[key]]

                        self.Lines[key].set_xdata(xData)
                        self.Lines[key].set_ydata(yData)

                        self.Axes[key].legend(loc='upper right', fontsize=8, framealpha=1, frameon=False)
                        self.Axes[key].set_ylabel(self.magnitudeMap[key]["Label"], fontproperties=FontConfig)
                        self.Axes[key].set_xlabel(self.magnitudeMap['t']["Label"], fontproperties=FontConfig)

                        if max(xData) - min(xData) < self.AxesLength:
                            self.Axes[key].set_xlim([0, self.AxesLength])
                        else:
                            self.Axes[key].set_xlim([max(xData) - self.AxesLength, max(xData)])
        except:
            pass

        self.draw()
        self.Figure.tight_layout()
        self.Figure.subplots_adjust(hspace=0.001)


class ASMAccelerometerPlot(ASMPlotCanvas):

    def __init__(self, *args, **kwargs):
        super(ASMAccelerometerPlot, self).__init__(*args, **kwargs)

        self.magnitudeMap = {
            "t": {
                "Name": "Time",
                "Label": "Time (s)",
            },
            "X": {
                "Color": "r-",
                "Name": "X angle",
                "Label": "X angle (deg)",
            },
            "Y": {
                "Color": "g-",
                "Name": "Y angle",
                "Label": "Y angle (deg)",
            },
            "Z": {
                "Color": "b-",
                "Name": "Z angle",
                "Label": "Z angle (deg)",
            },
        }

        self.AxesLength = 10
        self.Axes = {}

        self.Axes["X"] = self.Figure.add_subplot(3, 1, 1)
        self.Axes["X"].set_ylim(0, 450)
        self.Axes["X"].set_yticks([0, 90, 180, 270, 360])
        self.Axes["X"].set_xlim([0, self.AxesLength])
        self.Axes["X"].grid(True)

        self.Axes["Y"] = self.Figure.add_subplot(3, 1, 2, sharex=self.Axes["X"])
        self.Axes["Y"].set_ylim(0, 450)
        self.Axes["Y"].set_yticks([0, 90, 180, 270, 360])
        self.Axes["Y"].set_xlim([0, self.AxesLength])
        self.Axes["Y"].grid(True)

        self.Axes["Z"] = self.Figure.add_subplot(3, 1, 3, sharex=self.Axes["X"])
        self.Axes["Z"].set_ylim(0, 450)
        self.Axes["Z"].set_yticks([0, 90, 180, 270, 360])
        self.Axes["Z"].set_xlim([0, self.AxesLength])
        self.Axes["Z"].grid(True)

        xticklabels = self.Axes["X"].get_xticklabels() + self.Axes["Y"].get_xticklabels()
        pyplot.setp(xticklabels, visible=False)

        self.Lines = {}
        self.Lines["X"] = None
        self.Lines["Y"] = None
        self.Lines["Z"] = None

        self.Figure.tight_layout()
        self.Figure.subplots_adjust(hspace=0.001)


class ASMBarometerPlot(ASMPlotCanvas):

    def __init__(self, *args, **kwargs):
        super(ASMBarometerPlot, self).__init__(*args, **kwargs)

        self.magnitudeMap = {
            "t": {
                "Name": "Time",
                "Label": "Time (s)",
            },
            "T": {
                "Color": "r-",
                "Name": "Temperature",
                "Label": "Temperature (°C)",
            },
            "P": {
                "Color": "g-",
                "Name": "Pressure",
                "Label": "Pressure (mmHg)",
            },
        }

        self.AxesLength = 10
        self.Axes = {}

        self.Axes["T"] = self.Figure.add_subplot(2, 1, 1)
        self.Axes["T"].set_ylim(0, 100)
        self.Axes["T"].set_yticks([0, 20, 40, 60, 80])
        self.Axes["T"].set_xlim([0, self.AxesLength])
        self.Axes["T"].grid(True)

        self.Axes["P"] = self.Figure.add_subplot(2, 1, 2, sharex=self.Axes["T"])
        self.Axes["P"].set_ylim(0, 1000)
        self.Axes["P"].set_yticks([0, 200, 400, 600, 800])
        self.Axes["P"].set_xlim([0, self.AxesLength])
        self.Axes["P"].grid(True)

        xticklabels = self.Axes["T"].get_xticklabels()
        pyplot.setp(xticklabels, visible=False)

        self.Lines = {}
        self.Lines["T"] = None
        self.Lines["P"] = None

        self.Figure.tight_layout()
        self.Figure.subplots_adjust(hspace=0.001)


class ASMThermohygrometer(ASMPlotCanvas):

    def __init__(self, *args, **kwargs):
        super(ASMThermohygrometer, self).__init__(*args, **kwargs)

        self.magnitudeMap = {
            "t": {
                "Name": "Time",
                "Label": "Time (s)",
            },
            "T": {
                "Color": "r-",
                "Name": "Temperature",
                "Label": "Temperature (°C)",
            },
            "H": {
                "Color": "g-",
                "Name": "Humidity",
                "Label": "Humidity (%)",
            },
            "W": {
                "Color": "b-",
                "Name": "Dew Point",
                "Label": "Dew Point (°C)",
            },
        }

        self.AxesLength = 10
        self.Axes = {}

        self.Axes["T"] = self.Figure.add_subplot(3, 1, 1)
        self.Axes["T"].set_ylim(0, 100)
        self.Axes["T"].set_yticks([0, 20, 40, 60, 80])
        self.Axes["T"].set_xlim([0, self.AxesLength])
        self.Axes["T"].grid(True)

        self.Axes["H"] = self.Figure.add_subplot(3, 1, 2, sharex=self.Axes["T"])
        self.Axes["H"].set_ylim(0, 100)
        self.Axes["H"].set_yticks([0, 20, 40, 60, 80])
        self.Axes["H"].set_xlim([0, self.AxesLength])
        self.Axes["H"].grid(True)

        self.Axes["W"] = self.Figure.add_subplot(3, 1, 3, sharex=self.Axes["T"])
        self.Axes["W"].set_ylim(0, 100)
        self.Axes["W"].set_yticks([0, 20, 40, 60, 80])
        self.Axes["W"].set_xlim([0, self.AxesLength])
        self.Axes["W"].grid(True)

        xticklabels = self.Axes["T"].get_xticklabels() + self.Axes["H"].get_xticklabels()
        pyplot.setp(xticklabels, visible=False)

        self.Lines = {}
        self.Lines["T"] = None
        self.Lines["H"] = None
        self.Lines["W"] = None

        self.Figure.tight_layout()
        self.Figure.subplots_adjust(hspace=0.001)


class ASMUltrasonicPlot(ASMPlotCanvas):

    def __init__(self, *args, **kwargs):
        super(ASMUltrasonicPlot, self).__init__(*args, **kwargs)

        self.magnitudeMap = {
            "t": {
                "Name": "Time",
                "Label": "Time (s)",
            },
            "D": {
                "Color": "r-",
                "Name": "Distance",
                "Label": "Distance (cm)",
            },
        }

        self.AxesLength = 10
        self.Axes = {}

        self.Axes["D"] = self.Figure.add_subplot(1, 1, 1)
        self.Axes["D"].set_ylim(0, 200)
        self.Axes["D"].set_yticks([0, 50, 100, 150, 200])
        self.Axes["D"].set_xlim([0, self.AxesLength])
        self.Axes["D"].grid(True)

        self.Lines = {}
        self.Lines["D"] = None

        self.Figure.tight_layout()
        self.Figure.subplots_adjust(hspace=0.001)


class ASMUVRadiationPlot(ASMPlotCanvas):

    def __init__(self, *args, **kwargs):
        super(ASMUVRadiationPlot, self).__init__(*args, **kwargs)

        self.magnitudeMap = {
            "t": {
                "Name": "Time",
                "Label": "Time (s)",
            },
            "U": {
                "Color": "r-",
                "Name": "UV Intensity",
                "Label": "UV Intensity (mW/cm^2)",
            },
        }

        self.AxesLength = 10
        self.Axes = {}

        self.Axes["U"] = self.Figure.add_subplot(1, 1, 1)
        self.Axes["U"].set_ylim(0, 20)
        self.Axes["U"].set_yticks([0, 5, 10, 15, 20])
        self.Axes["U"].set_xlim([0, self.AxesLength])
        self.Axes["U"].grid(True)

        self.Lines = {}
        self.Lines["U"] = None

        self.Figure.tight_layout()
        self.Figure.subplots_adjust(hspace=0.001)

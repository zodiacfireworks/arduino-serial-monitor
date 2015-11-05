import sys
import serial
import datetime
import warnings

from pylab import *


def main():
    ion()
    figH = figure()
    axsH = figH.add_subplot(111)
    nData = 60
    xData = arange(0, nData)
    yData1 = nan*ones(nData)
    yData2 = nan*ones(nData)
    yData3 = nan*ones(nData)
    cData = 0

    plotLine1, = axsH.plot(xData, yData1, label="x")
    plotLine2, = axsH.plot(xData, yData2, label="y")
    plotLine3, = axsH.plot(xData, yData3, label="z")

    legend()

    axsH.set_ylim(22, 26)
    axsH.set_xlim(0, nData-1)
    show()

    try:
        time = datetime.datetime.now()
        fileName = 'serialData{0:%Y-%m-%dT%H:%M:%S.%f}.dat'.format(time)
        filePermissions = 'w'
        fileHandler = open(fileName, filePermissions)

        skipLines = 1

        serialMonitor = serial.Serial('/dev/ttyACM1', 9600)
        serialMonitor.flush()

        while serialMonitor.isOpen():

            line = serialMonitor.readline()
            line = line.decode("utf-8").strip('\r\n')

            if line and not skipLines:
                try:
                    line = line.split('|')
                    line = [item.split(':') for item in line]
                    # line = [(k, float(v)) for k, v in line]
                    line = [float(v) for k, v in line]

                    time = datetime.datetime.now()

                    print('{0:%Y-%m-%d %H:%M:%S.%f} {1: >10.2f} {2: >10.2f} {3: >10.2f}'.format(time, line[0], line[1], line[2]))
                    fileHandler.write('{0:%Y-%m-%dT%H:%M:%S.%f} {1: >10.2f} {2: >10.2f} {3: >10.2f}\n'.format(time, line[0], line[1], line[2]))

                    if cData <= nData-1:
                        yData1[cData] = line[0]
                        yData2[cData] = line[1]
                        yData3[cData] = line[2]
                    else:
                        xData[0:nData-1] = xData[1:]
                        xData[-1] = cData
                        yData1[0:nData-1] = yData1[1:]
                        yData2[0:nData-1] = yData2[1:]
                        yData3[0:nData-1] = yData3[1:]
                        yData1[-1] = line[0]
                        yData2[-1] = line[1]
                        yData3[-1] = line[2]

                        axsH.set_xlim(xData[0], xData[-1])

                    axsH.set_ylim(
                        floor(min([nanmin(yData1), nanmin(yData2), nanmin(yData3)]))-1,
                        ceil(max([nanmax(yData1), nanmax(yData2), nanmax(yData3)]))+1
                    )
                    cData += 1

                    plotLine1.set_xdata(xData)
                    plotLine1.set_ydata(yData1)
                    plotLine2.set_xdata(xData)
                    plotLine2.set_ydata(yData2)
                    plotLine3.set_xdata(xData)
                    plotLine3.set_ydata(yData3)
                    draw()
                    pause(0.001)

                except Exception as e:
                    raise(e)
                    # print(e)
            elif skipLines:
                skipLines -= 1

    except KeyboardInterrupt:
        print("\b\bBye-bee! :P")
        sys.exit()

if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        main()

import datetime
import pandas
import numpy
import pylab
import sys


def main():
    fileName = sys.argv[1]
    filePermissions = 'r'
    fileHandler = open(fileName, filePermissions)
    fileData = fileHandler.read().split('\n')
    time = numpy.empty(len(fileData), dtype=datetime.datetime)
    temp = numpy.empty(len(fileData), dtype=float)

    for i, line in enumerate(fileData):
        if line:
            line = line.split()
            print(line)
            time[i] = datetime.datetime.strptime(line[0], '%Y-%m-%dT%H:%M:%S.%f')
            temp[i] = float(line[1])

    timeSeries = pandas.Series(temp[0:-1], index=time[0:-1])

    print(timeSeries)
    timeSeries.plot()
    pylab.show()


if __name__ == '__main__':
    main()

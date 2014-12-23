# -*- coding: utf-8 -*-
'''
Created on 13.12.2014

@author: Shcheblykin
'''

#import math
#import numpy
import serial
import sys
import FileDialog  # для py2exe

#from matplotlib import mlab
from matplotlib import rc
from matplotlib import pyplot
from matplotlib import ticker

# Для работы кириллицы
font = {'family': 'Verdana', 'weight': 'normal'}
rc('font', **font)

class DSPdata():

    VERSION = u"1.01"
    DATE = u"13.12.2014"

    ## Имя COM-порта
    num = 4

    ## Буфер данных
    buf = []

    ## Класс COM-порта
    port = serial.Serial()

    ## Команда запроса данных
    com = "37"

    def __init__(self):
        pass

    def __str__(self):
        return u"Версия " + self.VERSION + ", " + self.DATE
        pass

    def setPort(self, num):
        ''' int -> None
        
            Устнановка номера используемого порта.
        '''
        try:
            s = serial.Serial(num - 1)
            s.close()
            self.num = num - 1
        except serial.SerialException, e:
            raise IOError
        pass

    def readPort(self):
        ''' None -> None
        
            Считывание данных из порта.
        '''
        try:
            s = serial.Serial(self.num, 115200, timeout=4)
        except serial.SerialException, e:
            raise IOError

        s.write(bytearray.fromhex(self.com))
        tmp = s.read(50000)


        for x in tmp:
            self.buf.append(x.encode('hex').upper())

        sys.stdout.write(u"Считано %d байт данных.\n" % len(self.buf))

        s.close()
        pass

    def printData(self):
        ''' None -> None
        
            Вывод данных из буфера на график.
        '''

        pyplot.xkcd()
        pyplot.xlabel(u'Номер отсчета')
        pyplot.ylabel(u'Уровень')
        pyplot.title(u'Данные DSP')

#        xlist = mlab.frange(xmin, xmax, xstep)

        # кол-во массивов данных в принятом буфере
        num = 6

        # массивы данных
        ydata = []
        for i in range(num):
            ydata.append([])

        # заполнение массивов данных (ось-Y) из буфера
        for i in range(0, len(self.buf) / (2 * num)):
            for j in range(0, num):
                # данные uint в буфере лежат в hex виде, младшим байтом вперед
                val = self.buf[i * 2 * num + j * 2 + 1]
                val += self.buf[i * 2 * num + j * 2]
                val = int(val, 16)
                ydata[j].append(val)

        # диапазон значений по оси-X
        xmin = 0
        xmax = len(ydata[0])
        xstep = 1
        xlist = range(xmin, xmax, xstep)

        pyplot.figure(1)

        for i in range(0, num):
            # 3 ряда, 2 строки, номер графика
            pyplot.subplot(num / 2, 2, i + 1)
            pyplot.grid()
            pyplot.plot(xlist, ydata[i], 'g', label=u"Данные")
            pyplot.title(u"Номер %d" % (i + 1))
#            pyplot.ylabel(u"Номер %d" % (i + 1))
            # небоьшое расширение диапазона выводимых значений
            dmin = min(ydata[i])
            dmax = max(ydata[i])
            dm = (dmax - dmin) * 0.05
            if (dmin != dmax):
                pyplot.ylim(dmin - dm, dmax + dm)
            dmax = int((xmax - xmin) * 0.02)
            pyplot.xlim(xmin - dmax, xmax + dmax)
            # отключение автоматического смещения по осям (например, для оси y
            # могло быть [1001, 1002, 1003] -> 1e3 + [1, 2, 3])
            pyplot.ticklabel_format(useOffset=False)
        pyplot.show()
        pass

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    ''' Считывание данных с указанного порта и вывод их на график.
        По умолчанию будет испоьзован порт COM4.
        Ключи:
        -p[name] - имя COM порта
    '''

    dspD = DSPdata()
    print unicode(dspD)

    port = 4

    # установка папаремтров заданных ключами
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]
        if arg[:2] == '-p':
            port = int(arg[2:])

    try:
        dspD.setPort(port)
    except:
        print u"Не удалось открыть порт COM" + str(port) + u"."
        sys.exit()

    try:
        dspD.readPort()
    except:
        print u"Не удалось считать данные."
        sys.exit()


    try:
        dspD.printData()
    except:
        print u"Не удалось вывести полученные данные на график."
        sys.exit()

    print u"Завершение работы."
    pass


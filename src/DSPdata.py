# -*- coding: utf-8 -*-
'''
Created on 13.12.2014

@author: Shcheblykin
'''

#import math
#import numpy
import serial
import sys
import time
import FileDialog  # для py2exe

#from matplotlib import mlab
from matplotlib import rc
from matplotlib import pyplot
from matplotlib import ticker
from matplotlib.widgets import Button, RadioButtons
from serial.tools import list_ports
#from PyQt4.Qt import right



# Для работы кириллицы
font = {'family': 'Verdana', 'weight': 'normal'}
rc('font', **font)

class DSPdata():

    VERSION = u"1.01"
    DATE = u"13.12.2014"

    ## Кол-во отображаемых графиков (массивов в принятом сообщении)
    NUMBER_PLOTS = 6

    ## Имя COM-порта
    num = 3

    ## Буфер данных
    buf = []

    ## Класс COM-порта
    port = serial.Serial()

    ## Команда запроса данных
    com = "37"

    ## Графики
    _line = []

    ## Оси ?!
    _ax = []

    ## График
    _fig = None

    ##
    def __init__(self):
        pass

    ##
    def __str__(self):
        return u"Версия " + self.VERSION + ", " + self.DATE

    ##
    def setPort(self, label):
        ''' (int) -> None
        
            Устнановка номера используемого порта.
        '''
        self.num = int(label[3:]) - 1
#        try:
#            s = serial.Serial(num - 1)
#            s.close()
#            self.num = num - 1
#        except serial.SerialException, e:
#            raise IOError

    #
    def findPorts(self):
        ''' (None) -> list of str
        
            Возвращает список доступных портов.
        '''
        return [x[0] for x in list_ports.comports()]

    ##
    def readPort(self):
        ''' (None) -> None
        
            Считывание данных из порта.
        '''
        self.buf[:] = []
        try:
            # timeout - максимальное время между принимаемыми символами
            s = serial.Serial(self.num, 115200, timeout=0.01)
        except serial.SerialException, e:
            raise IOError

        # очистка буфера приема
        s.flushInput()
        # отправка команды запроса
        s.write(bytearray.fromhex(self.com))

        print u"Чтение данных."

        while True:
            tmp = s.read()

            if len(tmp) == 0:
                break

            self.buf.append(tmp.encode('hex').upper())

        print u"Принято %d байт данных." % len(self.buf)

        s.close()

    ##
    def setupPlot(self):
        ''' (None) -> None
        
            Подготовка графиков к выводу.
        '''

#        pyplot.xkcd()  # Вид графика от руки
        self._fig = pyplot.figure(u"Данные DSP")

        self._ax[:] = []
        self._line[:] = []
        for i in range(self.NUMBER_PLOTS):
            a = self._fig.add_subplot(self.NUMBER_PLOTS / 2, 2, i + 1)
            pyplot.ylabel(u"Номер %d" % (i + 1))
            l, = a.plot([0], [0], 'g', label=u"Данные")
            self._ax.append(a)
            self._line.append(l)
            # отключение автоматического смещения по осям (например, для оси y
            # могло быть [1001, 1002, 1003] -> 1e3 + [1, 2, 3])
            pyplot.ticklabel_format(useOffset=False)
            pyplot.grid()

        pyplot.subplots_adjust(right=0.75)
        # добавление кнопки
#        pyplot.subplots_adjust(bottom=0.2)
#        axprev = pyplot.axes([0.7, 0.05, 0.1, 0.075])
#        axrefresh = pyplot.axes([0.81, 0.05, 0.1, 0.075])
        rax = pyplot.axes([0.80, 0.1, 0.15, 0.075])
        brefresh = Button(rax, u'Обновить', color=u'green', hovercolor=u'red')
        brefresh.on_clicked(self.refreshPlot)

        # добавление переключателя
        rax = pyplot.axes([0.80, 0.2, 0.15, 0.15])
        ports = self.findPorts()
        ports.sort()
        radio = RadioButtons(rax, ports)
        radio.on_clicked(self.setPort)
        self.setPort(radio.labels[0].get_text())

        pyplot.show()

    ##
    def clearPlot(self):
        ''' (None) -> None
         
            Очистка графиков.
        '''
        for i in range(self.NUMBER_PLOTS):
            self._line[i].set_data([0], [0])
            self._ax[i].set_ylim(0, 1)
            self._ax[i].set_xlim(0, 1)
        self._fig.canvas.draw()

    ##
    def refreshPlot(self, event=None):
        ''' () -> None
        
            Обработчик нажатия кнопки.
        '''
        self.clearPlot()
        self.readPort()
        self.printData()

    ##
    def printData(self):
        ''' None -> None
        
            Вывод данных из буфера на график.
        '''
#        xlist = mlab.frange(xmin, xmax, xstep)

        # массивы данных
        ydata = []
        for i in range(self.NUMBER_PLOTS):
            ydata.append([])

        # заполнение массивов данных (ось-Y) из буфера
        for i in range(0, len(self.buf) / (2 * self.NUMBER_PLOTS)):
            for j in range(0, self.NUMBER_PLOTS):
                # данные uint в буфере лежат в hex виде, младшим байтом вперед
                val = self.buf[i * 2 * self.NUMBER_PLOTS + j * 2 + 1]
                val += self.buf[i * 2 * self.NUMBER_PLOTS + j * 2]
                val = int(val, 16)
                ydata[j].append(val)

        # диапазон значений по оси-X
        xmin = 0
        xmax = len(ydata[0])
        xstep = 1
        xlist = range(xmin, xmax, xstep)

        for i in range(self.NUMBER_PLOTS):
#            # 3 ряда, 2 строки, номер графика
#            sub = pyplot.subplot(num / 2, 2, i + 1)
#            self._ax[i]
            self._line[i].set_data(xlist, ydata[i])

            # для графиков расположенных справа, подпись для y-оси выведем
            # справа
            if (i % 2) == 1:
                self._ax[i].yaxis.set_label_position("right")

            # небоьшое расширение диапазона выводимых значений
            if len(ydata[i]) != 0:
                dmin = min(ydata[i])
                dmax = max(ydata[i])
            else:
                dmin = dmax = 0
            if dmax != dmin:
                dm = (dmax - dmin) * 0.05
            elif dmax != 0:
                dm = dmax * 0.01
            else:
                dm = 1
            self._ax[i].set_ylim(dmin - dm, dmax + dm)

            if xmax != xmin:
                dmax = int((xmax - xmin) * 0.02)
            elif xmax != 0:
                dmax = dmax * 0.01
            else:
                dmax = 1
            self._ax[i].set_xlim(xmin - dmax, xmax + dmax)
#
        self._fig.canvas.draw()
#



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

#    try:
#        dspD.setPort(port)
#    except:
#        print u"Не удалось открыть порт COM" + str(port) + u"."
#        sys.exit()

#    try:
#        dspD.readPort()
#    except:
#        print u"Не удалось считать данные."
#        sys.exit()

    try:
        dspD.setupPlot()
    except:
        print u"Не удалось подготовить график."
        sys.exit()

#    try:
#        dspD.printData()
#    except:
#        print u"Не удалось вывести полученные данные на график."
#        sys.exit()

    print u"Завершение работы."


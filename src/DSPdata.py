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
import matplotlib
from matplotlib import rc
from matplotlib import numpy
from matplotlib import pyplot
from matplotlib import ticker
from matplotlib.backend_bases import NavigationToolbar2, Event
from matplotlib.widgets import Button, RadioButtons, CheckButtons, SpanSelector
from matplotlib.widgets import Cursor
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

    ## График исходных данных
    _axOriginal = None

    ## График изменяемый
    _axDinamic = None

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
    def checkPlot(self, label):
        ''' (Num) -> None
        
            Вкл./выкл. отображения графика по его номеру.
        '''
        num = int(label[-1]) - 1
        vis = not self._line[num].get_visible()
        self._line[num].set_visible(vis)
        print self._axDinamic.get_lines(),
        print self._axDinamic.get_lines()[num]
        self._axDinamic.get_lines()[num].set_visible(vis)
        self.onselect(-1, -1)
        self._fig.canvas.draw()

    ##
    def onselect(self, xmin=0, xmax=100000):
        ''' (Num, Num) -> None
        
            Действие при выборе диапазона.
        '''
        x = self._line[0].get_xdata()

        if len(x) == 0:
            return

        if xmin >= 0 and xmax >= 0:
            indmin, indmax = numpy.searchsorted(x, (xmin, xmax))

            xmin = max(0, int(xmin))
            xmax = min(len(x), int(xmax + 2))
        else:
            xmin = self._xlim[0]
            xmax = self._xlim[1]

        ymin = 100000
        ymax = -100000
        for i in range(1, self.NUMBER_PLOTS):
            line = self._line[i]
            if line.get_visible():
                ymin = min(ymin, min(line.get_ydata()[xmin:xmax]))
                ymax = max(ymax, max(line.get_ydata()[xmin:xmax]))
    #        self._axDinamic.cla()
    #
    #        for i in range(self.NUMBER_PLOTS):
    #            y = self._line[i].get_ydata()[xmin:xmax]
    #            l, = self._axDinamic.plot(thisx, y, '.-', lw=2, label=str(i + 1))
    #            l.set_visible(self._line[i].get_visible())

        self._xlim = [xmin, xmax - 1]
        self._ylim = [ymin, ymax]

        self._axDinamic.set_xlim(self._xlim)
        self._axDinamic.set_ylim(self._ylim)
        self._fig.canvas.draw()

    ##
    def setupPlot(self):
        ''' (None) -> None
        
            Подготовка графиков к выводу.
        '''

        def new_home(self, *args, **kwargs):
            ''' (xz, xz) -> None
            
                Обработчик события нажатия на кнопку "Reset original view."
                Применяется для подмены встроенного обработчика на "пустышку".
            '''
            s = 'home_event'
            event = Event(s, self)
#            event.foo = 100 # пример передачи параметра в обработчик
            self.canvas.callbacks.process(s, event)
#            NavigationToolbar2.home(self, *args, **kwargs)  # вызов оригинального обработчика

        def handle_home(evt):
            ''' (Event) -> None
                
                Установка границ отображения динамического графика в исходное
                состояние. Применяется при нажатии на кнопку "Reset original
                view".
            '''
            self._axDinamic.set_xlim(self._xlim)
            self._axDinamic.set_ylim(self._ylim)
            self._fig.canvas.draw()

        # подмена обработчика нажатия кнопки "Reset original view"
        NavigationToolbar2.home = new_home

#        pyplot.xkcd()  # Вид графика от руки
#        self._fig = pyplot.figure(u"Данные DSP")
        self._fig = pyplot.figure(u"Данные DSP")  # facecolor='white'
        self._fig.canvas.mpl_connect('home_event', handle_home)
        self._axDinamic = pyplot.subplot(2, 1, 2)
        pyplot.grid()
        self._axOriginal = pyplot.subplot(2, 1, 1)
        self._axOriginal.set_navigate(False)  # запрет изменения графика

        pyplot.axis('tight')
        for i in range(self.NUMBER_PLOTS):
            d = range(10)
            y = range(i, len(d) + i)
            l, = self._axOriginal.plot(d, y, '.-', lw=2, label=str(i + 1))
            self._axDinamic.plot(d, y, '.-', lw=2, label=str(i + 1))
            self._line.append(l)
        self.onselect()

        # loc='lower left', bbox_to_anchor=(1.0, 0.4),
        pyplot.legend(framealpha=0.5, fancybox=True)
        self._axOriginal.axis('auto')

        pyplot.grid()
        # отключение автоматического смещения по осям (например, для оси y
        # могло быть [1001, 1002, 1003] -> 1e3 + [1, 2, 3])
        pyplot.ticklabel_format(useOffset=False)
        # смещение области чертежа в форме
        pyplot.subplots_adjust(right=0.75)

        # добавление кнопки
        rax = pyplot.axes([0.80, 0.1, 0.15, 0.075])
        brefresh = Button(rax, u'Обновить', color=u'green',
                          hovercolor=u'yellow')
        brefresh.on_clicked(self.refreshPlot)

        # добавление переключателя для выбора COM-порта
        rax = pyplot.axes([0.80, 0.2, 0.15, 0.175])
        ports = self.findPorts()
        ports.sort()
        radio = RadioButtons(rax, ports)
        radio.on_clicked(self.setPort)
        self.setPort(radio.labels[0].get_text())

        # добавление выбора нужных графиков
        rax = pyplot.axes([0.80, 0.4, 0.15, 0.3])
        name = [u"График %d" % (x + 1) for x in range(self.NUMBER_PLOTS)]
        state = [True for x in range(self.NUMBER_PLOTS)]
        check = CheckButtons(rax, name, state)
        check.on_clicked(self.checkPlot)

        # мульти курсор
        cursor = Cursor(self._axDinamic, horizOn=False, useblit=True)

        # выбор диапазона
        self._span = SpanSelector(self._axOriginal, self.onselect, 'horizontal',
                            useblit=True, span_stays=True,
                            rectprops=dict(alpha=0.5, facecolor='red'))
        pyplot.show()

    ##
    def clearPlot(self):
        ''' (None) -> None
         
            Очистка графиков.
        '''
        d = range(1)
        for i in range(self.NUMBER_PLOTS):
            self._line[i].set_data(d, d)

        self._axOriginal.set_ylim(0, 1)
        self._axOriginal.set_xlim(0, 1)
        self._axDinamic.set_ylim(0, 1)
        self._axDinamic.set_xlim(0, 1)
        self._fig.canvas.draw()

    ##
    def refreshPlot(self, event=None):
        ''' () -> None
        
            Обработчик нажатия кнопки обновления графиков.
        '''
        try:
            self.clearPlot()
            dspD.readPort()
            self.printData()
        except:
            print u"Не удалось считать данные."


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
                # отрицательные числа
                if val >= 32768:
                    val = val - 65536;
                ydata[j].append(val)

        # диапазон значений по оси-X
        xmin = 0
        xmax = len(ydata[0])
        xstep = 1
        xlist = range(xmin, xmax, xstep)

        for i in range(self.NUMBER_PLOTS):
            self._line[i].set_data(xlist, ydata[i])
            self._axDinamic.get_lines()[i].set_data(xlist, ydata[i])

        xmax = 1
        ymax = 1
        ymin = 0
        if len(ydata[0]) != 0:
            xmax = max(xmax, len(ydata[i]))
            ymax = max(ymax, max([max(n) for n in ydata]))
            ymin = min(ymin, min([min(n) for n in ydata]))
        self._axOriginal.set_xlim(0, xmax)
        ymin = (ymin * 1.05) if ymin < 0 else (ymin * 0.05)
        ymax = (ymax * 0.95) if ymax < 0 else (ymax * 1.05)
        self._axOriginal.set_ylim(ymin, ymax)
        self.onselect(-1, -1)
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
    dspD.setupPlot()
#    except:
#        print u"Не удалось подготовить график."
#        sys.exit()

#    try:
#        dspD.printData()
#    except:
#        print u"Не удалось вывести полученные данные на график."
#        sys.exit()

    print u"Завершение работы."


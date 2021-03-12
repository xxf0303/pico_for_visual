from tkinter import *
from tkinter import scrolledtext
import scipy.signal as signal
# plt嵌入tkinter
#matplotlib.use('Agg')  # 该模式下绘图无法显示，plt.show()也无法作用
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
import matplotlib.pyplot as plt
import numpy as np
import time

class WinToPico(object):

    def __init__(self, fs=250, VRange=2, duration=15E-5):
        self.root = Tk()
        self.root.geometry("1000x650")
        self.root.title("PICO-Reading Mode")
        self.root.resizable(width=False, height=False)

        self.entry = Entry(self.root)
        self.picoinfo = scrolledtext.ScrolledText(self.root, width=45, height=3)
        self.saminfo = scrolledtext.ScrolledText(self.root, width=45, height=3)
        self.text = scrolledtext.ScrolledText(self.root, width=30, height=34)  # 滚动文本框（宽，高（以行数为单位））
        self.writeTxt()

        self.phase = (60.0,90.0)
        self.address = ('E:\A.txt',  'E:\B.txt')

        # self.im = PIL.Image.open("E:/waves_pico/save.jpg")
        # self.img = ImageTk.PhotoImage(self.im)
        # imLabel = Label(self.root, image=self.img).place(x=270, y=50)

        self.entry.place(x=260, y=595, height=41, width=670)
        self.text.place(x=10, y=10)  # 滚动文本框在页面的位置
        self.picoinfo.place(x=260, y=5)
        self.saminfo.place(x=600, y=5)

        # 创建按钮
        button = Button(self.root, text='读取', command=self.btn_def)
        button.place(x=950,y=600)

        b_Quit = Button(self.root, text='退出', bg='brown', fg='white', command=self.root.quit)
        b_Quit.place(x=950, y=13)

        self.picoinfo.insert("insert", "READING MODE:"'\n')
        self.picoinfo.insert("insert", "Reading from the text given."'\n')
        self.picoinfo.insert("insert", '\n')

        self.root.mainloop()

    #每次按键更新一次
    def btn_def(self):
        start = time.perf_counter()

        var = self.entry.get()
        ph_var = var.split(' ')
        self.address = (ph_var[0], ph_var[1])

        k = 2
        tmp = self.loadDatadet(self.address[0], k)

        self.dataTimeAxis = np.array(tmp[0])
        self.dataA = np.array(self.loadDatadet(self.address[1], k)[1])
        self.dataB = np.array(tmp[1])

        end=time.perf_counter()
        readfromtT = end-start
        self.saminfo.tag_config('tag', foreground='red')
        self.saminfo.insert("insert", "time for reading data from txt:", 'tag')
        self.saminfo.insert("insert",readfromtT,'tag')
        self.saminfo.insert("insert", " s", 'tag')
        self.saminfo.insert("insert", '\n')


        start = time.perf_counter()

        self.newfig()
        self.update_txt()

        end = time.perf_counter()
        drawT= end - start
        self.saminfo.insert("insert", "time for drawing plt:", 'tag')
        self.saminfo.insert("insert",drawT,'tag')
        self.saminfo.insert("insert", " s", 'tag')
        self.saminfo.insert("insert", '\n')

        self.show_pic()

    def newfig(self):
        b_home = Button(self.root, text='还原', command=self.zoom_home)
        b_home.place(x=90, y=520, width=30)

        b_In = Button(self.root, text='放大', command=self.zoom_in)
        b_In.place(x=90, y=480, width=30)

        b_Out = Button(self.root, text='缩小', command=self.zoom_out)
        b_Out.place(x=90, y=560, width=30)

        b_L = Button(self.root, text='←', command=self.zoom_left)
        b_L.place(x=50, y=520, width=30)

        b_R = Button(self.root, text='→', command=self.zoom_right)
        b_R.place(x=130, y=520, width=30)

        Label(self.root, text='phase=').place(x=20, y=605)
        self.e_ph = Entry(self.root)
        self.e_ph.place(x=75, y=605, width=70)
        b_ph = Button(self.root, text='设定', command=self.setphase)
        b_ph.place(x=160, y=600, width=30)

    def setphase(self):
        start = time.perf_counter()

        var = self.e_ph.get()
        if var != '':
            ph_var=var.split('-')

            self.phase = ( float(ph_var[0]), float(ph_var[1]) )
        print(self.phase)

        self.saminfo.insert("insert", "Reading one period…"'\n')

        tmp = self.readOnePeriod(self.dataTimeAxis, self.dataA, self.dataB)

        self.fig2 = plt.figure()
        self.fig2.canvas.mpl_connect('scroll_event', self.call_back)
        ax1 = plt.subplot(3, 1, 1)  # 截取幕布的一部分
        ax1.plot(tmp[0], tmp[1])
        plt.grid() #标出格线

        ax2 = plt.subplot(3, 1, 2)
        ax2.plot(tmp[0], tmp[2])
        plt.grid()
        print(self.phase[0])
        print("T=",tmp[3])
        print("tmp=",tmp[0][0])

        x1 = (self.phase[0]*tmp[3])/360.00 + tmp[0][0]
        x2 = (self.phase[1]*tmp[3])/360.00 + tmp[0][0]
        print(x1,'\n')
        print(x2, '\n')

        data_filted = self.Lfilt(tmp[2])
        pulse = self.getOnePulse(tmp[0],data_filted)

        ax3 = plt.subplot(3, 1, 3)
        ax3.plot(pulse[0], pulse[1])
        plt.grid()

        ax1.axvline(x=x1, ls="--", c="red")  # 添加垂直直线
        ax1.axvline(x=x2, ls="--", c="red")  # 添加垂直直线
        ax2.axvline(x=x1, ls="--", c="red")  # 添加垂直直线
        ax2.axvline(x=x2, ls="--", c="red")  # 添加垂直直线

        end = time.perf_counter()
        drawT= end - start
        self.saminfo.insert("insert", "time for capturing the pulse:", 'tag')
        self.saminfo.insert("insert",drawT,'tag')
        self.saminfo.insert("insert", " s", 'tag')
        self.saminfo.insert("insert", '\n')

        plt.legend()
        self.fig2.show()

    def call_back(self, event):
        print(event)
        print('\n')
        axtemp = event.inaxes
        x_min, x_max = axtemp.get_xlim()
        print("xM,xm")
        print((x_min, x_max))

        fanwei = (x_max - x_min) / 10
        print(fanwei)
        print((x_min + fanwei, x_max - fanwei))
        print('\n''\n')
        if event.button == 'up':
            axtemp.set(xlim=(x_min + fanwei, x_max - fanwei))
            print('up')
        elif event.button == 'down':
            axtemp.set(xlim=(x_min - fanwei, x_max + fanwei))
            print('down')
        self.fig2.canvas.draw_idle()  # 绘图动作实时反映在图像上

    def zoom_left(self):
        Scp = (self.currX_Max - self.currX_Min) * 0.25
        xs = self.currX_Min - Scp
        xe = self.currX_Max - Scp

        self.ax2.set(xlim=(xs, xe))
        self.ax1.set(xlim=(xs, xe))

        self.currX_Min = xs
        self.currX_Max = xe

        print('left')
        self.fig.canvas.draw_idle()  # 绘图动作实时反映在图像上

    def zoom_home(self):
        xs = self.dataTimeAxis[0]*1000
        xe = self.dataTimeAxis[len(self.dataTimeAxis)-1]*1000
        self.ax2.set(xlim=(xs, xe))
        self.ax1.set(xlim=(xs, xe))

        self.currX_Min = xs
        self.currX_Max = xe

        print('还原')
        print((xs, xe))
        self.fig.canvas.draw_idle()  # 绘图动作实时反映在图像上

    def zoom_right(self):
        Scp = (self.currX_Max - self.currX_Min) * 0.25
        xs = self.currX_Min + Scp
        xe = self.currX_Max + Scp

        self.ax2.set(xlim=(xs, xe))
        self.ax1.set(xlim=(xs, xe))

        self.currX_Min = xs
        self.currX_Max = xe

        print('right')
        self.fig.canvas.draw_idle()  # 绘图动作实时反映在图像上

    def zoom_in(self):
        Scp = (self.currX_Max - self.currX_Min)*0.25
        xs = (self.currX_Max + self.currX_Min)*0.5 - Scp
        xe = (self.currX_Max + self.currX_Min)*0.5 + Scp

        self.ax2.set(xlim=(xs, xe))
        self.ax1.set(xlim=(xs, xe))

        self.currX_Min = xs
        self.currX_Max = xe

        print('up')
        print((xs, xe))
        self.fig.canvas.draw_idle()  # 绘图动作实时反映在图像上

    def zoom_out(self):
        Scp = (self.currX_Max - self.currX_Min)
        xs = (self.currX_Max + self.currX_Min)*0.5 - Scp
        xe = (self.currX_Max + self.currX_Min)*0.5 + Scp

        self.ax2.set(xlim=(xs, xe))
        self.ax1.set(xlim=(xs, xe))

        self.currX_Min = xs
        self.currX_Max = xe

        print('down')
        self.fig.canvas.draw_idle()  # 绘图动作实时反映在图像上

        print((xs,xe))


    def show_pic(self):
        # b1 = [1, 2, 3, 4]
        # a1 = [i * 1000 for i in b1]
        # y1 = [-3, 0, 5, 6]
        # y2 = [6, 7, 2, 3]
        a1 = [i * 1000 for i in self.dataTimeAxis]
        y1 = self.dataA
        y2 = self.dataB
        self.currX_Min = self.dataTimeAxis[0]*1000
        self.currX_Max = self.dataTimeAxis[len(self.dataTimeAxis)-1]*1000

        self.fig = plt.figure(figsize=(7, 5))
        # self.fig.canvas.bind("<MouseWheel>", self.call_back)
        # self.fig.canvas.mpl_connectbind("<MouseWheel>", self.call_back)

        self.ax1 = plt.subplot(2, 1, 1)  # 截取幕布的一部分
        self.ax1.xaxis.set_major_formatter(plt.NullFormatter())  # 取消x轴坐标
        self.ax1.plot(a1, y1)
        self.ax1.grid()
        self.ax1.set_ylabel("ChA-Vol(V)")

        self.ax2 = plt.subplot(2, 1, 2)
        self.ax2.plot(a1, y2)
        self.ax2.grid()

        self.ax2.set_ylabel("Ch-Vol(V)")
        self.ax2.set_xlabel("Time (ms)")


        canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        #canvas.bind("<MouseWheel>", self.call_back)

        canvas.draw()
        canvas.get_tk_widget().place(x=260,y=60)

    def addLine(self,x1, x2):
        self.ax1.axvline(x=x1, ls="--", c="red")  # 添加垂直直线
        self.ax1.axvline(x=x2, ls="--", c="red")  # 添加垂直直线
        self.ax2.axvline(x=x1, ls="--", c="red")  # 添加垂直直线
        self.ax2.axvline(x=x2, ls="--", c="red")  # 添加垂直直线

    def update_txt(self):
        self.saminfo.insert("insert", "phase = ")
        self.saminfo.insert("insert", self.phase)
        self.saminfo.insert("insert", "（角度制）"'\n')

    def readOnePeriod(self, dataT, dataA, dataB):
        size = len(dataT)
        print("!!!size= ",size)
        per = size//40

        absA = list(map(abs, dataA))

        zero = min(absA)
        isZ = False
        noZnum = 0
        zeroX = []
        for i in range(len(absA)):
            if (absA[i] == zero) & (isZ == False):
                zeroX.append(i)
                isZ = True
                noZnum = 0
            elif (absA[i] != zero) & isZ:
                noZnum += 1
                if noZnum > per:
                    isZ = False
                    noZnum = 0
            elif (absA[i] == zero) & isZ:
                noZnum = 0

        print(zeroX)

        if (dataA[int((zeroX[0] + zeroX[1]) / 2)]) > 0:
            l = 0
        else:
            l = 1

        print(l)
        print(dataA[zeroX[0] + zeroX[1]])
        aimA = dataA[zeroX[l]: (zeroX[l + 2])]  # + 10000)]
        aimB = dataB[zeroX[l]: (zeroX[l + 2])]  # + 10000)]
        aimX = dataT[zeroX[l]: (zeroX[l + 2])]  # + 10000)]
        T = dataT[zeroX[l + 2]] - dataT[zeroX[l]]

        return (aimX, aimA, aimB, T)

    def Lfilt(self, data):
        # 创建order3低通道butterworth过滤器：
        b, a = signal.butter(3, 0.05)
        # 将过滤器应用于xn。使用lfilter_zi选择过滤器的初始条件：
        zi = signal.lfilter_zi(b, a)
        z, _ = signal.lfilter(b, a, data, zi=zi * data[0])

        return z

    def getOnePulse(self, dataT, data):
        minV = min(data)
        maxV = max(data)
        scope = maxV - minV

        isLow = False
        isHigh = False
        noLnum = 0
        noHnum = 0
        lowX = []
        highX = []
        m = 0
        for i in range(len(data)):

            if ((data[i] - minV) <= 0.2 * scope) & (isLow == False):
                lowX.append(i)
                isLow = True
                noLnum = 0
                m += 1
            elif ((data[i] - minV) > 0.2 * scope) & isLow:
                noLnum += 1
                if noLnum > 50:
                    isLow = False
                    noLnum = 0
            elif ((data[i] - minV) <= 0.2 * scope) & isLow:
                noLnum = 0

            if ((maxV - data[i]) <= 0.2 * scope) & (isHigh == False):
                highX.append(i)
                isHigh = True
                noHnum = 0
                m += 1
            elif ((maxV - data[i]) > 0.2 * scope) & isHigh:
                noHnum += 1
                if noHnum > 50:
                    isHigh = False
                    noHnum = 0
            elif ((maxV - data[i]) <= 0.2 * scope) & isLow:
                noHnum = 0

        print("high: ", highX)
        print("low: ", lowX)

        numT = highX[1] - highX[0]
        print("num of T=   ", numT)

        start = lowX[0] + numT // 2
        end = start + numT

        aimA = data[start:end]  # + 10000)]
        aimX = dataT[start:end]  # + 10000)]
        T = dataT[end] - dataT[start]
        print("timeT=   ", T)

        return (aimX, aimA, T)

    def writeTxt(self):
        self.text.tag_config('tag', foreground='brown')
        self.text.tag_config('tag2', foreground='red')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "目前已有的命令："'\n')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "E:\digital4ChA.txt E:\digital4ChB.txt", 'tag')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "双通道txt文件地址，中间一个空格隔开"'\n''\n')

        self.text.insert("insert", "phase=60-90", 'tag')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "相位区间"'\n''\n')

        self.text.insert("insert", "注意（请严格按照规则输入，否则可能出现各种未知错误！！！）："'\n', 'tag2')
        self.text.insert("insert", "1.每个语句必须用空格隔开；"'\n')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "2.如若参数没有变化，可直接执行而不输入语句；"'\n')
        self.text.insert("insert", "\n")

    def loadDatadet(self, infile, k):
        print("in to")
        f = open(infile, 'r')
        sourceInLine = f.readlines()
        dataset1 = []
        dataset2 = []
        y = []
        x = []
        for line in sourceInLine:
            temp1 = line.strip('\n')
            temp2 = temp1.split(' : ')
            dataset1.append(temp2[1])
            dataset2.append(temp2[0])
        for i in range(0, len(dataset1)):
            y.append(float(dataset1[i]))

        for i in range(0, len(dataset2)):
            x.append(float(dataset2[i]))

        return (x, y)

if __name__ == '__main__':
    WinToPico()

    #print(A1.fs)
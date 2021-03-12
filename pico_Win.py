from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from picoscope import ps2000
from picoscope import ps2000a
from picoscope import picobase

import numpy as np
import pandas as pd
import openpyxl
import os
import time

import scipy.signal as signal

from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from tkinter import scrolledtext
import tkinter.messagebox as messagebox


class WinToPico():
    def __init__(self, fs=250, VRange=2.0, duration=15E-2):
        self.fs = fs
        self.nSamples = 10000
        self.actualSamplingInterval = 1E-6

        self.root = Tk()
        self.root.title('Pico 2000b')
        self.root.geometry("1000x650")
        self.root.resizable(width=False, height=False)

        self.entry = Entry(self.root)
        self.picoinfo = scrolledtext.ScrolledText(self.root, width=45, height=3)
        self.saminfo = scrolledtext.ScrolledText(self.root, width=45, height=3)
        self.text = scrolledtext.ScrolledText(self.root, width=30, height=34)  # 滚动文本框（宽，高（以行数为单位））
        self.writeTxt()

        self.fs = fs
        self.VRangeA = VRange
        self.VRangeB = VRange
        self.duration = duration
        self.phase = (60.0, 90.0)
        self.actualSamplingInterval = 1E-6

        self.entry.place(x=260, y=595, height=41, width=670)
        self.text.place(x=10, y=10)  # 滚动文本框在页面的位置
        self.picoinfo.place(x=260, y=5)
        self.saminfo.place(x=600, y=5)

        # 创建按钮
        button = Button(self.root, text='设定', command=self.btn_def)
        button.place(x=950, y=600)

        b_Quit = Button(self.root, text='退出', bg='brown', fg='white', command=self.root.quit)
        b_Quit.place(x=950, y=13)

        self.root.mainloop()

    #每次按键更新一次
    def btn_def(self):

        self.picoinfo.insert("insert", "Attempting to open Picoscope 2000..."'\n')
        self.ps = ps2000a.PS2000a()
        self.picoinfo.insert("insert", "Found the following picoscope:"'\n')
        s = self.ps.getAllUnitInfo()
        self.picoinfo.insert("insert", s)
        self.picoinfo.insert("insert", '\n')

        # 从输入框中读取fs和VRange
        i = 0
        var = self.entry.get()
        size = len(var)

        fs_var = ""
        VR_var = ""
        VR_varB = ""
        VR_varA = ""
        dura_var = ""
        ph_var1 = ""
        ph_var2 = ""

        while i < size - 1:
            if var[i:i + 2] == 'fs':
                i = i + 3
                for j in range(i, size):
                    if var[j] != ' ':
                        fs_var = ''.join([fs_var, var[j]])
                    else:
                        i = i + 1
                        break
                    i = i + 1

            elif var[i:i + 7] == 'VRangeA':
                i = i + 8
                for j in range(i, size):
                    if var[j] != ' ':
                        VR_varA = ''.join([VR_varA, var[j]])
                    else:
                        i = i + 1
                        break
                    i = i + 1

            elif var[i:i + 7] == 'VRangeB':
                i = i + 8
                for j in range(i, size):
                    if var[j] != ' ':
                        VR_varB = ''.join([VR_varB, var[j]])
                    else:
                        i = i + 1
                        break
                    i = i + 1

            elif var[i:i + 6] == 'VRange':
                i = i + 7
                for j in range(i, size):
                    if var[j] != ' ':
                        VR_var = ''.join([VR_var, var[j]])
                    else:
                        i = i + 1
                        break
                    i = i + 1

            elif var[i:i+6]=='TRange':
                i = i + 7
                for j in range(i,size):
                    if var[j]!=' ':
                        dura_var = ''.join([dura_var,var[j]])
                    else:
                        i=i+1
                        break
                    i=i+1

            elif var[i:i + 5] == 'phase':
                i = i + 6
                for j in range(i, size):
                    if (var[j] != ' ') & (var[j] != '-'):
                        ph_var1 = ''.join([ph_var1, var[j]])
                    else:
                        i = i + 1
                        break
                    i = i + 1
                for j in range(i, size):
                    if (var[j] != ' '):
                        ph_var2 = ''.join([ph_var2, var[j]])
                    else:
                        i = i + 1
                        break
                    i = i + 1

            else:
                print("错误命令！")
                self.text.insert("insert", "错误命令！")
                self.text.insert("insert", '\n')
                break

        if fs_var != '':
            self.fs = int(fs_var)
        if VR_var != '':
            self.VRangeA = float(VR_var)
            self.VRangeB = float(VR_var)
        if VR_varA != '':
            self.VRangeA = float(VR_varA)
        if VR_varB != '':
            self.VRangeB = float(VR_varB)
        if dura_var != '':
            self.duration = float(dura_var)
        if (ph_var1 != '') & (ph_var2 != ''):
            self.phase = (float(ph_var1), float(ph_var2))


        self.samplingSet(self.fs, self.VRangeA, self.VRangeB, self.duration)
        self.read2txt()

        self.update_txt()
        self.show_pic()
        self.newfig()

        self.ps.stop()
        self.ps.close()

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

        tmp = self.readOnePeriod(self.dataTimeAxis, self.dataA, self.dataB)

        self.fig2 = plt.figure()
        self.fig2.canvas.mpl_connect('scroll_event', self.call_back)

        ax1 = plt.subplot(3, 1, 1)  # 截取幕布的一部分
        ax1.plot(tmp[0], tmp[1])
        plt.grid() #标出格线

        ax2 = plt.subplot(3, 1, 2)
        ax2.plot(tmp[0], tmp[2])
        plt.grid()

        data_filted = self.Lfilt(tmp[2])
        pulse = self.getOnePulse(tmp[0],data_filted)

        ax3 = plt.subplot(3, 1, 3)
        ax3.plot(pulse[0], pulse[1])
        plt.grid()

        x1 = (self.phase[0] * tmp[3]) / 360.00 + tmp[0][0]
        x2 = (self.phase[1] * tmp[3]) / 360.00 + tmp[0][0]
        print(x1, '\n')
        print(x2, '\n')

        ax1.axvline(x=x1, ls="--", c="red")  # 添加垂直直线
        ax1.axvline(x=x2, ls="--", c="red")  # 添加垂直直线
        ax2.axvline(x=x1, ls="--", c="red")  # 添加垂直直线
        ax2.axvline(x=x2, ls="--", c="red")  # 添加垂直直线

        end=time.perf_counter()
        sampleT = end-start
        self.saminfo.tag_config('tag', foreground='red')
        self.saminfo.insert("insert", "time for capturing the pulse:", 'tag')
        self.saminfo.insert("insert",sampleT,'tag')
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

    def show_pic(self):
        start = time.perf_counter()

        a1 = [i * 1000 for i in self.dataTimeAxis]
        y1 = self.dataA
        y2 = self.dataB
        self.currX_Min = self.dataTimeAxis[0]*1000
        self.currX_Max = self.dataTimeAxis[len(self.dataTimeAxis)-1]*1000
        self.fig = plt.figure(figsize=(7, 5))

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
        # canvas.bind("<MouseWheel>", self.call_back)

        canvas.draw()
        canvas.get_tk_widget().place(x=260, y=60)

        end=time.perf_counter()
        sampleT = end-start
        self.saminfo.tag_config('tag', foreground='red')
        self.saminfo.insert("insert", "time for drawing:", 'tag')
        self.saminfo.insert("insert",sampleT,'tag')
        self.saminfo.insert("insert", " s", 'tag')
        self.saminfo.insert("insert", '\n')

        # x1 = self.phase[0] * np.pi / 180
        # x2 = self.phase[1] * np.pi / 180


    def zoom_home(self):
        xs = self.dataTimeAxis[0]*1000
        xe = self.dataTimeAxis[len(self.dataTimeAxis)-1]*1000
        self.ax2.set(xlim=(xs, xe))
        self.ax1.set(xlim=(xs, xe))

        self.currX_Min = xs
        self.currX_Max = xe

        print('还原')
        print((xs,xe))
        self.fig.canvas.draw_idle()  # 绘图动作实时反映在图像上

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

        dataTimeAxis = np.arange(10) * 7
        print(dataTimeAxis)

        print((dataTimeAxis[0],dataTimeAxis[9]))


    def update_txt(self):

        self.saminfo.insert("insert", "Now,Fs = ")
        self.saminfo.insert("insert", self.fs)
        self.saminfo.insert("insert", "MHz"'\n')

        self.saminfo.insert("insert", "VRange(A) = ")
        self.saminfo.insert("insert", self.VRangeA)
        self.saminfo.insert("insert", "V"'\n')

        self.saminfo.insert("insert", "VRange(B) = ")
        self.saminfo.insert("insert", self.VRangeB)
        self.saminfo.insert("insert", "V"'\n')
        #
        # self.saminfo.insert("insert", "phase = ")
        # self.saminfo.insert("insert", self.phase)
        # self.saminfo.insert("insert", "（角度制）"'\n')

    # 写左侧文字
    def writeTxt(self):
        self.text.tag_config('tag', foreground='brown')
        self.text.tag_config('tag2', foreground='red')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "目前已有的命令："'\n')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "fs=100", 'tag')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "单位MHz(采样频率)"'\n')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "VRange=2", 'tag')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "单位V(两通道测量范围)"'\n')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "VRangeA=2", 'tag')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "单位V(通道A测量范围)"'\n')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "VRangeB=2", 'tag')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "单位V(通道B测量范围)"'\n')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "TRange=0.15", 'tag')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "单位ms(采样时间)"'\n')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "phase=60-90", 'tag')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "相位区间"'\n''\n')

        self.text.insert("insert", "注意（请严格按照规则输入，否则可能出现各种未知错误！！！）："'\n', 'tag2')
        self.text.insert("insert", "1.每个语句必须用空格隔开；"'\n')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "2.如若个采样参数没有变化，可直接执行而不输入语句；"'\n')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "3.请保证一次命令输入中，\nVRange 和 VRangeA或VRangeB\n不同时出现；"'\n')
        self.text.insert("insert", "\n")
        self.text.insert("insert", "4.可用的fs:20,50,100,150,200"'\n')
        self.text.insert("insert", "如输入其他的fs值，不会报错，但实际fs为上述值中，距离输入fs最接近的一值。"'\n')

    def samplingSet(self, fs=250.0, VRangeA=2.0, VRangeB=2.0, duration=15E-2):
        start = time.perf_counter()

        obs_duration = duration * 0.001
        sampling_interval = 1.0/(fs*1000000)

        (self.actualSamplingInterval, self.nSamples, maxSamples) = \
            self.ps.setSamplingInterval(sampling_interval, obs_duration)

        self.saminfo.insert("insert", "Sampling interval = %f ns" % (self.actualSamplingInterval * 1E9))
        self.saminfo.insert("insert", '\n')
        self.saminfo.insert("insert", "Taking  samples = %d" % self.nSamples)
        self.saminfo.insert("insert", '\n')
        self.saminfo.insert("insert", "Maximum samples = %d" % maxSamples)
        self.saminfo.insert("insert", '\n')
        print("Sampling interval = %f ns" % (self.actualSamplingInterval * 1E9))
        print("Taking  samples = %d" % self.nSamples)
        print("Maximum samples = %d" % maxSamples)

        # the setChannel command will chose the next largest amplitude
        channelRangeA = self.ps.setChannel('A', 'DC', VRangeA, 0.0, enabled=True,
                                     BWLimited=False)
        channelRangeB = self.ps.setChannel('B', 'DC', VRangeB, 0.0, enabled=True,
                                           BWLimited=False)

        self.ps.setSigGenBuiltInSimple(offsetVoltage=0, pkToPk=1.2, waveType="Sine",
                                  frequency=50E3)

        self.saminfo.insert("insert","Chosen channel range = %d" % channelRangeA)
        self.saminfo.insert("insert", '\n')
        self.saminfo.insert("insert","Chosen channel range = %d" % channelRangeB)
        self.saminfo.insert("insert", '\n')
        print("Chosen channel range = %d" % channelRangeA)
        print("Chosen channel range = %d" % channelRangeB)

        self.ps.setSimpleTrigger('A', 0.05, 'Falling', timeout_ms=100, enabled=True)
        self.ps.setSimpleTrigger('B', 0.05, 'Falling', timeout_ms=100, enabled=True)

        end=time.perf_counter()
        sampleT = end-start
        self.saminfo.tag_config('tag', foreground='red')
        self.saminfo.insert("insert", "time for sampling-setting:", 'tag')
        self.saminfo.insert("insert",sampleT,'tag')
        self.saminfo.insert("insert", " s", 'tag')
        self.saminfo.insert("insert", '\n')

        #AWG setting
        #self.ps.setSigGenBuiltInSimple(offsetVoltage=0, pkToPk=1.2, waveType="Sine",
                                  #frequency=50E3)

    def read2txt(self):
        start = time.perf_counter()

        self.ps.runBlock()
        self.ps.waitReady()
        self.saminfo.insert("insert","Waiting for awg to settle."'\n')
        print("Waiting for awg to settle.")

        time.sleep(2.0)
        self.ps.runBlock()
        self.ps.waitReady()
        self.saminfo.insert("insert", "Done waiting for trigger"'\n')
        print("Done waiting for trigger")

        self.dataA = self.ps.getDataV('A', self.nSamples, returnOverflow=False)
        self.dataB = self.ps.getDataV('B', self.nSamples, returnOverflow=False)

        self.dataTimeAxis = np.arange(self.nSamples) * self.actualSamplingInterval
        self.currX_Min = self.dataTimeAxis[0]
        self.currX_Max = self.dataTimeAxis[self.nSamples-1]

        self.ps.stop()
        self.ps.close()

        end=time.perf_counter()
        readT=end-start
        self.saminfo.tag_config('tag', foreground='red')
        self.saminfo.insert("insert", "time for reading data:", 'tag')
        self.saminfo.insert("insert",readT,'tag')
        self.saminfo.insert("insert", " s", 'tag')
        self.saminfo.insert("insert", '\n')

        # Uncomment following for call to .show() to not block
        # plt.ion()
        start = time.perf_counter()

        data1 = dict(zip(self.dataTimeAxis, self.dataA))
        filename1 = open('E:\data1.txt', 'w')  # dict转txt

        for k, v in data1.items():
            filename1.write(str(k))
            filename1.write(" ")
            filename1.write(':')
            filename1.write(" ")
            filename1.write(str(v))
            filename1.write('\n')

        filename1.close()

        data2 = dict(zip(self.dataTimeAxis, self.dataB))
        filename2 = open('E:\data2.txt', 'w')  # dict转txt

        for k, v in data2.items():
            filename2.write(str(k))
            filename2.write(" ")
            filename2.write(':')
            filename2.write(" ")
            filename2.write(str(v))
            filename2.write('\n')

        filename2.close()

        end=time.perf_counter()
        writeT=end-start
        self.saminfo.tag_config('tag', foreground='red')
        self.saminfo.insert("insert", "time for writing data to txt:", 'tag')
        self.saminfo.insert("insert",writeT,'tag')
        self.saminfo.insert("insert", " s", 'tag')
        self.saminfo.insert("insert", '\n')

        # plt.figure()
        # #plt.hold(True)
        # plt.plot(dataTimeAxis, dataA, label="Clock")
        # plt.grid(True, which='major')
        # plt.title("Picoscope 2000 waveforms")
        # plt.ylabel("Voltage (V)")
        # plt.xlabel("Time (ms)")
        # plt.legend()
        # plt.show()

    def readOnePeriod(self, dataT, dataA, dataB):
        absA = list(map(abs, dataA))
        size = len(dataT)
        per = size // 40

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
        aimA = dataA[zeroX[0]: (zeroX[2] )]#+ 10000)]
        aimB = dataB[zeroX[0]: (zeroX[2] )]#+ 10000)]
        aimX = dataT[zeroX[0]: (zeroX[2] )]#+ 10000)]
        T = dataT[zeroX[2]] - dataT[zeroX[0]]

        return (aimX, aimA, aimB, T)

    def Lfilt(self, data):
        b, a = signal.butter(3, 0.05)
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

if __name__ == '__main__':

    A1 = WinToPico()

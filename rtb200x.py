# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 21:40:21 2018

@author: sixtimesseven

Quick script to read rtb200 data and perform fft on multiple channels with more points
Oscilloscope needs to be set up, acuisition memory needs to be set, and I recomend to take a single shot 
before running the data.

I use anaconda + the following dependencies:
    pyvisa
    matplotlib
    numpy
    
If you use Spyder and want the plot to pop out you have to set:
    Tools > preferences > IPython console > Graphics > Graphics backend > Backend: Automatic
    
"""

import visa
import matplotlib.pyplot as plt
import numpy
import time

class tools:
    def fftPlot(channel, start, stop):  
        rm = visa.ResourceManager()
        my_instrument = rm.open_resource('TCPIP::192.168.0.99::INSTR')
        
        #Set number of Data Points
        my_instrument.write('CHANnel' + str(channel) + ':DATA:POINts MAXimum')
        
        #Get the Data setup for the cannel
        #RTB2004 Manual page 366
        ch1DataS = my_instrument.query('CHANnel' + str(channel) + ':DATA:HEADer?')
        ch1DataS = ch1DataS.split(",")
        ch1DataS = list(map(float, ch1DataS))
        ch1StartTime = ch1DataS[0]
        ch1StopTime = ch1DataS[1]
        ch1RecordLength = ch1DataS[2]
        ch1NumberOfValuesPerSample = int(ch1DataS[2])
        
        #Get Data from RTB200x
        ch1Data = my_instrument.query('CHANnel' + str(channel) + ':DATA?')
        
        #Get Data Format right
        ch1Data = ch1Data.replace('"','');
        ch1Data = ch1Data.replace(' ','');
        ch1Data = ch1Data.replace('ins,C' + str(channel) + 'inV','')
        ch1Data = ch1Data.replace('\r\n',',')
        ch1Data = ch1Data[:-2]
        ch1Data = ch1Data.split(',')
        ch1Data.pop(0)
        ch1Data.pop(0)
        
        #Split into a timestamp and a measurment array
        timeStamp = list()
        measurment = list()
        c = 0
        for i in range(ch1NumberOfValuesPerSample):
            timeStamp.append(float(ch1Data[c]))
            measurment.append(float(ch1Data[c+1]))
            c = c + 2
        
        #Calculate fft xAxis
        dt = (timeStamp[ch1NumberOfValuesPerSample-1] - timeStamp[0]) / ch1NumberOfValuesPerSample
        maxF = int(1/dt)
        t = list()
          
        #Calculate and fft
        fftData = numpy.fft.rfft(measurment)
        fftData = numpy.asarray(fftData)
        fftR = numpy.real(fftData)
        fftC = numpy.real(fftData)
        fftData = numpy.power( (numpy.sqrt(numpy.power(fftR, 2) + numpy.power(fftC, 2))), 2)
        
        
        #Calculate xAxis Frequencies to plot xAxis  
        t = numpy.fft.rfftfreq(ch1NumberOfValuesPerSample, dt)
        
        #Get max frequency value to plot
        maxT = 0
        while 1:
            if(t[maxT] >= stop):
                break
            maxT = maxT + 1        
        minT = 1 
        while 1:
            if(t[minT] >= start):
                break
            minT = minT + 1
            
        #Plot FFT data
        plt.show(block=True)
        plt.plot(t[minT:maxT], fftData[minT:maxT])


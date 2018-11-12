# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 13:02:35 2018

@author: sixtimesseven

Quick script to read rtb200x data and perform fft on multiple channels with more points
Oscilloscope needs to be set up, acuisition memory needs to be set, and I recomend to take a single shot 
before running the data.

I use anaconda + the following dependencies:
    pyvisa
    matplotlib
    numpy
    
If you use Spyder and want the plot to pop out you have to set:
    Tools > preferences > IPython console > Graphics > Graphics backend > Backend: Automatic
    
Sstart and stop frequency only affects plotting!
    
"""
import matplotlib.pyplot as plt
import rtb200x

ip = '192.168.50.3'
low = 4000
high = 40000


def main():
    plt.show(block=True)
    #get fft of channels 
    #fftPlot(channel, start plot from frequency [Hz], stop plotting at frequency [Hz])
    rtb200x.tools.fftPlot(ip,1,low,high)
    #rtb200x.tools.fftPlot(ip,2,1,9ik,/100)-\]
    #rtb200x.tools.fftPlot(ip,3,1,100)
    #rtb200x.tools.fftPlot(ip,4,1,100)
    
    #show all acumulated plots
    plt.show()


if __name__ == "__main__":
    main()
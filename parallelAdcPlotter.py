# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 21:40:21 2018

@author: sixtimesseven

Short script to read and plot Parallel Bus data from the RTB2000 Logic
Channels.
Setup the parallel decoder manually #TODO automatic 
Usefull for parallel ADCs with fixed sampling rate...

I use anaconda, python3.6 and (usually) the following dependencies:
    pyvisa
    matplotlib
    numpy
    scipy
    
If you use Spyder and want the plot to pop out and display properly you have to set:
    Tools > preferences > IPython console > Graphics > Graphics backend > Backend: Automatic
    
Use however you like. But do not blame me if you break stuff!    
"""
import visa
import matplotlib.pyplot as plt
import numpy as np
import time
import cmath
from scipy import signal

###############################################################################################
#USER PARAMETERS
###############################################################################################

ipOscilloscope      = '192.168.50.3'    #IP oscilloscope
busWidth            = 12                #Width of dataBus
clockBit            = 12                #Address of clock bit
clocked             = 0                 #0 for Parallel, 1 for Parallel Clocked

###############################################################################################
#NO USER PARAMETERS BYOND THIS POINT ;)
###############################################################################################


def main(ipOsc, bW, cB, cp):
    if cp is 1:
        cl = 'C'
    else:
        cl = ''
        
    #connect the instruments
    rm = visa.ResourceManager()
    rtb = rm.open_resource('TCPIP::' + str(ipOsc) + '::INSTR')
    

    #Allow long scpi tcip timeouts
    rtb.timeout = 5000
    
    #TODO Solve the hole setup via user parameters
    #TODO do a *rst maybe
    #rtb.write('BUS1:CPARallel:WIDTh ' + str(bW))
    #rtb.write('BUS1:CPARallel:CLOCk:SOURce D' + str(cB))
    #rtb.write('BUS1:CPARallel:CS:ENABle OFF')

    #Get number of points
    nop = int(rtb.query('BUS1:' + cl + 'PARallel:FCOunt?'))
    
    #Get all decoded data
    dataPackage = np.zeros(nop)
    dataTimestamp = np.zeros(nop)
    for i in range(nop): #check if the frame status is ok, if not, skip and print warning
        state = str(rtb.query('BUS1:' + cl + 'PARallel:FRAMe' + str(i) + ':STATE?'))
        if(state.find('K',0,3) is 0):
            print('ERROR, package: '+str(i) +' is invalid!!!')         
        else: #if valid, read into array
            dataPackage[i] = float(rtb.query('BUS1:' + cl + 'PARallel:FRAMe' + str(i) + ':DATA?').replace('\n',''))
            dataTimestamp[i] = float(rtb.query('BUS1:' + cl + 'PARallel:FRAMe' + str(i) + ':START?').replace('\n',''))
  
    plt.plot(dataTimestamp, dataPackage)
    plt.show()


if __name__ == "__main__":
    main(ipOscilloscope, busWidth, clockBit, clocked)





      
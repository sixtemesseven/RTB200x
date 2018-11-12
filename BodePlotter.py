# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 21:40:21 2018

@author: sixtimesseven

Bode plotter using RTB2004 series oscilloscope and sdg2000x series function generator via TCIP.
Connect channel 1 of function generator to DUT input. Channel 1 of oscilloscope to DUT output and Channel 3 of oscilloscope to channel 
two of function generator. 

You can configure start and stop frequency as well as number of points to measure. Low frequencies can take quiet a while...

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
import numpy
import time
import cmath
from scipy import signal

###############################################################################################
#USER PARAMETERS
###############################################################################################

ipOscilloscope      = '192.168.50.3' #IP oscilloscope
ipSiglentFuGen      = '192.168.50.5' #IP FuGen

measurmentPoints    = 200            #Number of meas. points 
startFrequency      = 1000000        # Start Frequency
stopFrequency       = 60000000       #Stop Frequency
amplitudeIn         = 1              #Amplitude in at DUT
numberOfSamples     = 100            #Number of samples to average
mode                = 'Log'          #Measurment point / plotting (Lin / Log)

###############################################################################################
#NO USER PARAMETERS BYOND THIS POINT ;)
###############################################################################################

#TODO snc out. phase of fugen (please lets all ask Rich from RS / eevblog as many times as possible)
#TODO Logarithmic options
#TODO calculate log result for amplitude plot

def main(ipOsc, ipSdg, points, start, stop, ampIn, nOS, m):
    #connect the instruments
    rm = visa.ResourceManager()
    rtb = rm.open_resource('TCPIP::' + str(ipOsc) + '::INSTR')
    sdg = rm.open_resource('TCPIP::' + str(ipSdg) + '::INSTR')
    
    #Allow long scpi tcip timeouts
    rtb.timeout = 50000
    sdg.timeout = 50000
    
    #Set Signal Source (identical channel 1 and 2 settings)
    for ch in range(1,3,1):
        sdg.write('*RST;*WAI') #Reset
        sdg.write('C'+str(ch)+':BSWV WVTP, Sine') #Set to Sine
        sdg.write('C'+str(ch)+':BSWV FRQ, 10kj0') #Set to Sine
        sdg.write('C'+str(ch)+':BSWV AMP,'+str(ampIn)) #Set to 2Vpp
        sdg.write('C'+str(ch)+':BSWV PHSW, 0') #Set Phase 0
        sdg.write('C1:OUTP Load, 50') #50ohm impeadance to dut
        sdg.write('C2:OUTP Load, HZ') #High Z to reference input
        sdg.write('C'+str(ch)+':Outp On') #Switch both on
    
    ##Setup RTB
    #Set Slot 1 to phase measurment
    rtb.write('*RST;*WAI') #Reset
    rtb.write('CHAN1:STATE ON') #channels on
    rtb.write('CHAN3:STATE ON')
    rtb.write('CHAN1:Coupling ACLimit') #Ac couple channels
    rtb.write('CHAN3:Coupling ACLimit')
    rtb.write('CHAN1:RANGE'+str(ampIn*0.9)) #Set a range
    rtb.write('CHAN3:RANGE'+str(ampIn*0.9))
    rtb.write('TRIGger:A:CH3') #Trigger on reference channel
    rtb.write('TRIGger:A:FINDlevel') #Autoset trigger level
    rtb.write('MEAS1:SOUR CH1,CH3') #Setup measurments phase
    rtb.write('MEAS1:Main Phase') 
    rtb.write('MEAS2:SOUR CH1')  #Setup measurments pp Amplitude
    rtb.write('MEAS2:Main PEAK')
    rtb.write('MEAS3:SOUR CH3')  #Setup measurments pp Amplitude
    rtb.write('MEAS3:Main PEAK')
    rtb.write('CHAN:TYPE HRES') #Set high resolution mode
    rtb.write('MEASurement1:STATistics On') #Enable statistics
    rtb.write('PROBe3:SETup:ATTenuation:MANual 1') #Directly conect fugen ch2 to ch3 of rtb2004 via 50ohm bnc. FuGen set to HZ
    rtb.write('TRIGger:A:SOURce CH3') #Set trigger to channel 3
    rtb.write('ACQuire:SEGMented: ON') #Fast segmentation mode on
    
    #Set reference channel range
    rtb.write('CHAN3:RANGE '+str(ampIn*1.2)+';*WAI')
        
    #data array def
    phase = list()
    xAxis = list()
    ampRel = list()
    imaginary = list()
    
    logSpace = numpy.exp(numpy.linspace(numpy.log(start), numpy.log(stop), points))
    
    #Measurment loop
    for p in range(1,points+1,1):
        rtb.write('ACQuire:NSINgle:COUNt 1') #only average one value for now
        
        if m is 'Lin':
            pF = int(start + ((stop-start)/points*p)) #current test frequency
        if m is 'Log':
            pF = logSpace[p-1]
        xAxis.append(pF)
            
        #Set Function Generator to new value
        sdg.write('C1:BSWV FRQ,'+str(pF))
        sdg.query('C2:BSWV FRQ,'+str(pF)+';*OPC?')
        
        #Get Data from rtb200x
        rtb.query('SING;*OPC?')
        
        rtb.write('Timebase:Range ' +str(1/pF*5)) #Set time scale to get 5 cycles to measure
        rtb.write('CHAN1:OFFS 0') #Set channel into middle
        rtb.write('CHAN3:OFFS 0;*OPC')
        
        #Scale range to max for max ADC resolution, needs sometimes 3 tries before it is correct... #TODO find a faster way      
        i = 1
        while i is not 0:
            if int(rtb.query('STATus:QUEStionable:ADCState:CONDition?')) is not 0: #Check if ADC is clipping on a channel
                i = i + 1
            rtb.write('ACQuire:NSINgle:COUNt 5') #Read 5 times 
            rtb.write('SING;*WAI')
            vCH1 = float(rtb.query('MEAS2:RES:AVG?'))
            rtb.write('CHAN1:RANGE '+str(vCH1*1.2))
            i = i - 1 
        rtb.write('ACQuire:NSINgle:COUNt 1') #Single Acuisition. Waits until completed. Use "instrument.timeout = 50000" (!) 

        '''    
        ##Old approach, the one above works much better and is faster. But AUToset is even slower... For reference...
        #Scale down verticals if they clip
        while 1:
            rtb.query('SING;*OPC?')
            adcState =int(rtb.query('STATus:QUEStionable:ADCState:CONDition?')) #Upper and Lower ADC clipping indicator
            flag = 0   
            if adcState &0b01 is not 0 or adcState &0b10 is not 0: #Clipping on CH1?
                vScalCH1 = float(rtb.query('CHAN1:RANGE?').rstrip())
                rtb.write('CHAN1:RANGE '+str(vScalCH1*1.1))
                flag = 1
                print('scale 1')
            if adcState &0b010000 is not 0 or adcState &0b100000 is not 0:
                vScalCH3 = float(rtb.query('CHAN3:RANGE?').rstrip())
                rtb.write('CHAN3:RANGE '+str(vScalCH3*1.1))
                flag = 1
            if flag is 0: #exit loop when no clipping has been indicated
                break
        '''
    
        #Acuisition
        rtb.write('ACQuire:NSINgle:COUNt '+str(nOS)) #Single Acuisition. Waits until completed. Use "instrument.timeout = 50000" (!)        
        rtb.query('Runsingle;*OPC?')
        phaseR = float(rtb.query('MEAS1:RES:AVG?')) #Get phase angle and limit to +-180degree
        if phaseR < -180:
            phaseR = -180
        if phaseR > 180:
            phaseR = 180
        phase.append(phaseR) #Read averaged values back     
        ampRel.append(float(rtb.query('MEAS2:RES:AVG?')) / float(rtb.query('MEAS3:RES:AVG?')))

    #Plot Results    
    #In two Subplots
    plt.subplot(2, 1, 1)
    plt.plot(xAxis, ampRel)
    plt.title('Amplitude')
    plt.ylabel('[dB]')  
    if m is 'Log':
       plt.xscale('log') 
    plt.yscale('log') 
    
    plt.subplot(2, 1, 2)
    plt.plot(xAxis, phase)
    plt.xlabel('Phase')
    plt.ylabel('[deg]') 
    if m is 'Log':
       plt.xscale('log')    
        
    plt.savefig('frequencyResponse_'+str(start)+'_'+str(stop)+'_'+str(points)+'.jpg')
    plt.show()

if __name__ == "__main__":
    main(ipOscilloscope, ipSiglentFuGen, measurmentPoints, startFrequency, stopFrequency, amplitudeIn, numberOfSamples, mode)





      
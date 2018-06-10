#!/usr/bin/env python3

#https://github.com/MrBiz/PiFan
#Author: G Soffe (MrBiz)

import time
import os
import configparser
import RPi.GPIO as GPIO
from datetime import datetime

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_UP)

config = configparser.ConfigParser()
config.read("/usr/local/sbin/fan/fan.config")
interval = int(config.get('CPU_fan', 'interval'))
Frequency = float(config.get('CPU_fan', 'Frequency'))
SpeedStep = int(config.get('CPU_fan', 'SpeedStep'))
TargetTemp = float(config.get('CPU_fan', 'TargetTemp'))
MaxTemp = float(config.get('CPU_fan', 'MaxTemp'))
MinOnDutycycle = int(config.get('CPU_fan', 'MinOnDutycycle'))

#set initial variable states
RPM = 0
FanState = 0
Dutycycle = 0
x = 0
LastTemp =  TargetTemp

#Establish the fan driver
Pulse = GPIO.PWM(8, Frequency)
Pulse.start(0)

# Procedure to count RPM pulses
def count(channel):
    global x
    x = x + 1

# add RPM Pulse event
GPIO.add_event_detect(10, GPIO.RISING, callback=count)

def SpeedUp(dc):
    dc = dc + SpeedStep
    if dc>100: #Limit DutyCycle
        dc = 100
    elif dc<MinOnDutycycle: #Make sure fan starts at minimum Dutycycle
        dc = MinOnDutycycle
        
    #print('going up')
    Pulse.ChangeDutyCycle(dc) #raise Dutycycle
    #print (dc,"% Duty")            
    return dc #return new Dutycycle

def SpeedDown(dc):
    dc = dc - SpeedStep
    if dc<0:    #prevent -Dutycycle error
        dc = 0
    elif dc<MinOnDutycycle: #If the Dutycycle falls below the minimum the fan turns off.
        dc = 0
        
    #print('going down')
    Pulse.ChangeDutyCycle(dc) #lower dutycycle
    #print (dc,"% Duty")
    return dc #return new Dutycycle

def getCPUtemperature():
    CPUtemp = os.popen('vcgencmd measure_temp').readline() #query OS for CPUtemp
    CPUtemp = float(CPUtemp.replace("temp=","").replace("'C\n","")) #remove all text and convert to Float
    return CPUtemp #return float

def KickStart(): #spin up fan for lower dutycycles that cannot start the fan spinning without a boost
    #print('Kick Start')
    Pulse.ChangeDutyCycle(50)
    time.sleep(1)
    FanState = 1
    return()


try:
  while True :
    temp = getCPUtemperature()
    #print(temp, "C")

    #Get RPM
    x = 0
    time.sleep(1)
    RPM = int(((x /2) /1) *60)
    #End RPM
    #print(RPM, "RPM")

    # check if the fan running?
    if RPM>0:
        FanState = 1
    else:
        FanState = 0
    
    if temp>TargetTemp: #is cpu hot?
        if temp>=MaxTemp: #is cpu VERY hot?
            Dutycycle = 100 #Set Max Duty
            Dutycycle = SpeedUp(Dutycycle) #Spin fan and return the new Dutycycle
        elif temp>LastTemp: #if CPU is not VERY hot, but is it hotter than when we last tested it?
                if FanState==0: #is the fan off
                    KickStart() #Kick start the fan
                    Dutycycle = SpeedUp(Dutycycle) #Spin fan and return the new Dutycycle
                else:
                    Dutycycle = SpeedUp(Dutycycle) #If the fan is alredy spinning, just set a higher Dutycycle
        elif temp<(((MaxTemp - TargetTemp) / 2) + TargetTemp): #is the temp in lower temp range
            if temp<LastTemp: #is it still cooling down
                Dutycycle = SpeedDown(Dutycycle) #turn the fan down a bit
    elif temp<TargetTemp: #is the CPU cool
        if FanState==1: #is the fan on
            Dutycycle = SpeedDown(Dutycycle)

    #set the new fan state
    if Dutycycle>0:
        FanState = 1
    else:
        FanState = 0
        
    LastTemp =  temp #set the last known CPU 

    dt =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(dt,",", temp, "C ,", Dutycycle,"% Duty ,", RPM, "RPM")
    
    time.sleep(interval) #wait for the fan to do it's work for a bit.

except KeyboardInterrupt:
  Pulse.stop()
  GPIO.cleanup()

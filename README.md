# PiFan

V1.0

Raspberry Pi CPU fan software control for 3 wire (with controller) or 4 wire fans (without controller).

This is a Pulse Width Modulation (PWM) fan controller for load and temperature monitored fan control for the Raspberry Pi.  
Note: this may work with 2 wire fans (with controller) but it won't have RPM monitoring. I haven't tested that setup yet though.

# Installation:

1) Copy all files to: /usr/local/sbin/fan/

2) Run 'sudo chmod 755 /usr/local/sbin/fan/*'

3) Copy file 'cpufan' to /etc/init.d/

4) Run the command 'sudo update-rc.d cpufan defaults' to install the service.

The defaults should work but if you need to, you can change the settings in the configuration file 'fan.config' 

Install your heatsink on the Raspberry Pi CPU
Mount your fan on the top of your heatsink

# Controller:

You will need:

  * A 5 volt 3 wire fan.
  * An NPN transister: **BC549C** -  Bipolar (BJT) Single Transistor, NPN, 30 V, 250 MHz, 625 mW, 100 mA, 500 hFE 
  
I used this 30v one because it was the smallest I could get at the time, best practice is to use a resister between the transisters Base & GPIO14 (pin 8) as well but mine has been going for over a year without one and no issues so 'meh'.
  
 * Connect the red fan wire to GPIO5V (pin 4)
  
 * Connect the yellow fan wire (RPM Sensor) to GPIO15 (pin 10)
  
 * Connect the black fan wire to the Transisters collector (C)
  
 * Connect the Transisters Emmitter (E) to GPIOGround (pin 6)
  
 * Connect the Transisters Base (B) to GPIO14 (pin 8)
  
 **See 'ControllerDiag.png' for example**
 
  
If all is good you should should hear the fan run up to full speed for about 2 seconds on boot, then it will slow as the service takes control.

As always, use at your own risk.

MrBiz.

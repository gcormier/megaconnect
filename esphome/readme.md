# ESPHome installation guide

Precondition: You have all the [required hardware for the ESPHome controller](https://). 

## Preparation and Configuration
* Get Python and install it: https://www.python.org/downloads/. On Windows, add Python to the PATH variable of your Computer. 
* Download [esphome.yaml](https://github.com/gcormier/megaconnect/blob/main/esphome/megadesk.yaml), [esphome.h](https://github.com/gcormier/megaconnect/blob/main/esphome/megadesk.h) and [esphome.cpp](https://github.com/gcormier/megaconnect/blob/main/esphome/megadesk.cpp). 
* In esphome.yaml replace the values of the parameters ssid and password with the correct values for your WLAN router. Both values need to be enclosed with `""`. The value for the board parameter needs to be  "d1_mini", without quotes.
* On Windows download https://cdn.sparkfun.com/assets/learn_tutorials/5/9/7/Windows-CH340-Driver.zip and install it - it's an USB driver needed for Windows to communicate with the ESP board. 
* Connect the ESP board to your PC via a Micro-USB cable. 

## Build and Installation
* Open a (cmd) shell to install ESPHome in your Python (runtime) environment. Run
_pip3 install wheel
pip3 install esphome_
* From the shell compile and install the ESPHome package on your ESP microcontroller: 
_esphome run megadesk.yaml_
* At the end of the installation procedure, the MAC address of the ESP microcontroller is printed to the consolse. Add it to your DHCP server and link it to an IP address in your WLAN (xxx.xxx.xxx.xxx). Alternative: You could also set a fixed IP address in the yaml configuration. 
* Once done, restart your ESP microcontroller and point a browser to http://xxx.xxx.xxx.xxx to get access to the control interface

## Keep in mind
* ESPHome does not offer HTTPs support. This means, communication between the client app and the ESP board is unencrypted. 
* You could add a username/password protection to the webserver to add a certain level of protection, however, as basicauth is used, passwords are not encrypted and transported over non-encrypted http. 
* So bottom line: Consider your megadesk to be publicly acccessible, at least within your WLAN. 

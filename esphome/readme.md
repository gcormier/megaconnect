# ESPHome installation guide

* In esphome.yaml replace the ssid and the password with the correct values from your WLAN router. Both values need to be enclosed with `""`. If you use `"` within your password, you have to escape it with `\"`. Value for the board parameter needs to be  "d1_mini" without quotes.
* Download https://cdn.sparkfun.com/assets/learn_tutorials/5/9/7/Windows-CH340-Driver.zip and install it - it's an USB driver needed for Windows to communicate with the ESP board. 
* Connect the ESP board to your PC via a Micro-USB cable. 
* Get Python and install it: https://www.python.org/downloads/windows/. Add Python to the PATH variable of your Windows Computer. 
* Open a windows cmd shell to install ESPHome in your Python (runtime) environment. Run
_pip3 install wheel
pip3 install esphome_
* From the cmd compile and install the ESPHome package on your ESP microcontroller: 
_esphome run megadesk.yaml_
* At the end of the installation (once it is complete), you can find the MAC address of the ESP microcontroller. Add it to your DHCP server and link it to an IP address (xxx.xxx.xxx.xxx). 
Alternative: You could also set a fixed IP address in the yaml configuration. 
* Once done, restart your ESP microcontroller and point a browser to http://xxx.xxx.xxx.xxx to get access to the control interface

Keep in mind:
* ESPHome does not offer HTTPs support (reason: limited cpu power). This means, communication between the client app and the ESP board is unencrypted. 
* You could add a username/password protection to the webserver to add a certain level of protection, however, as basicauth is used, passwords are not encrypted and transported over non-secure http. 
* So bottom line: Consider your megadesk to be publicly acccessible, at least within your LAN. 

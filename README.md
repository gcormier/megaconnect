# MegaConnect
MegaConnect is a systray app allowing to  control an ESPHome enhanced Megadesk directly from the desktop. It is available for Windows, MacOS and Linux.

[What is megadesk?](https://github.com/gcormier/megadesk/)

[What is ESPHome?](https://esphome.io/)

[What is an ESPHome enhanced megadesk?](https://medium.com/@matthiasschaffer/make-your-ikea-standing-desk-smart-62b8307da8b6)

## Main Features
* Define one-click-actions to move your table to any pre-configured position (height) you like
* Define one-click-actions to make your table automatically change its height following what ever pattern you like (i.e. 30 min sitting, 30 min standing,... )

<img  src="/docs/screenshot_megaconnect.png" width=55%/>

## Preconditions
* A Megadesk installed on your Bekant table. You can order your Megadesk on [Tindies](https://www.tindie.com/products/gcormier/megadesk/).
* An ESPHome enabled microcontroller connected to your Megadesk. [How to get your own ESPHome controller](https://). 
* Windows (10 and higher) or MacOS or Linux
* A Python runtime environment. Python can be downloaded from [python.org](https://www.python.org/downloads/).
* For Windows users alternatively a [binary](https://github.com/gcormier/megaconnect/binary) is provided which does not require a Python installation

## Installation

### Windows
On Windows, user can either run the Python Script or use the Binary. **Binary is recommended** for users not familiar with Python. 
#### Binary
* Download the MegaConnect Binary from https://github.com/gcormier/megaconnect/binary.
* Customize the configuration file `megaconnect.conf` inside the application directory.
* To run MegaConnect, execute `MegaConnect.exe` inside the application directory.
* You can also add a shortcut to  "MegaConnect.exe" to your Windows autostart directory to automatically start it with Windows.

#### Python
* Download MegaConnect from https://github.com/gcormier/megaconnect/. 
* Customize the configuration file `megaconnect.conf` inside the application directory.
* Run `setup.py` from the commandline inside the application directory. Make sure all required Python modules are correctly installed. 
* To start MegaConnect run `python megaconnect.py`. 

### MacOS
#### Binary
No binaries are currently provided for MacOS. 
#### Python
While MegaConnect is expected to run on MacOS, it has not yet been tested and no installation procedure is documented atm. 

If you plan to run MegaConnect on MacOS, need some support and are willing to contribute to the project, please get in contact with the developers. 

### Linux
#### Binary
No binaries are currently provided for Linux. 
#### Python
While MegaConnect is expected to run on Linux, it has not yet been tested and no installation procedure is documented atm.

If you plan to run MegaConnect on Linux, need some support and are willing to contribute to the project, please get in contact with the developers. 


## Configuration
The MegaConnect configuration file needs to be called [megaconnect.conf](https://github.com/gcormier/megaconnect/blob/main/src/megaconnect.conf) and has to be stored in the same directory as the MegaConnect application. A configuration template can be found in the related directory. 

During startup of the application, the configuration file is checked. A missing configuration file, incomplete and/or invalid configuration parameter will result in MegaConnect refusing to start and throwing a related error. Error messages are either sent to the system's standard error output and/or to the MegaConnect logfile (megaconnect.log) located in the application's directory. 

The configuration file contains the following configuration sections and parameter:

### [network]
**url**

DNS or IP address of the esphome device controlling megadesk.

Examples:
* url=http://megadesk.myhome.com
* url=http://192.168.0.20

### [step]
**step**

Defines the fixed distance to move the table up or down with a single click on the related up or down button. 
Value needs to be an integer in the range of 139 to 6640, where 139 approx equals 1.32 cm/0.52 inches
step=139

Example:
* step=139

### [positions]
List of positions that can be triggered from megaconnect. A position can either be a memory position in megadesk, a height in cm or a height in inches.

Format: **height=description**

where **height** has one of the following formats:
* for stored positions: **p[Number of memory position in megadesk]**. Valid value range: all stored positions in megadesk. Please take into account that the first memory position on megadesk is number 2 (so there is no "p1="). If megadesk's memory is lost or reset, these positions will not work. It's therefore recommended to use one of the two following configuration options:
* for height in cm: **c[height in cm]**. Valid value range: 59-118, only integers allowed.
* for height in inches: **i[height in inches]** Valid value range: 23-47, only integers.

The description is used as label on the megaconnect menu.

Examples:
* p2=Sitting Position 
* p3=Standing Position 
* c74=Medium Height 
* c60=Low Rider
* i25=Chill Height
* i45=Wakeup Height

### [intervals]
List of interval configurations to automatically move the desk into different positions (height).

Format: **interval=pos1:pos2:pos3:description**

where

* interval defines the waiting time between position changes in seconds (must be a positive integer)
* pos1, pos2, .... defines the positions the table has to be moved to in the given order
* description is used as label on the MegaConnect Auto Position Change submenu
 
An unlimited number of positions can be configured, each needs to be separate by `:` and the description always has to be the last element in the list.
 
Positions can be configured as
* stored positions: p[Number of memory position in megadesk]. Valid range: all stored positions in megadesk.
* a height in cm: c[height in cm]. Valid range: 59-118, only integers.
* a height in inches: i[height in inches]. Valid range: 23-47, only integers.

The description is used as label on the MegaConnect menu.

Examples:
* 900=c65:c105:15min sit stand
* 1800=p2:i27:c105:30min low mid hi

### [logging]
Logging is always on, however the log level can be set. By default only CRITICAL is logged, for normal operations the log level can be set to INFO, for error tracking DEBUG can be chosen.

Examples:
* loglevel = INFO
* loglevel = DEBUG

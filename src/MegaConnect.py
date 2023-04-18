import configparser
import logging
import os.path
import sys
import threading
import time
import webbrowser
import PIL.Image
import requests
import validators
import re

from threading import Event
from threading import Thread
from pystray import Icon
from pystray import Menu
from pystray import MenuItem

# remove tracebacks for privacy reasons in binary distributions
sys.tracebacklimit = 0

# A class that extends the Thread class
class AutoMoveTimerThread(Thread):
    # override the constructor
    def __init__(self, interval, act_sequence, event, bekant_url):
        Thread.__init__(self)
        self.interval = interval
        # action_sequence is a list of at least two positions, which AutoMove is using to control the positioning
        self.act_sequence = act_sequence
        self.event = event
        self.bekant_url = bekant_url

    # override the run function
    def run(self):
        logger.debug(str(threading.get_ident()) + ": AutoMoveTimerThread started")
        # integer which points to the index in the action_sequence to define the next action from the action_sequence
        # list to be executed. On initialize always start with the first element in the list
        next_move_action = 0

        # run forever, stopping is done by stopping the thread from the control process via a shared event
        while True:
            # trigger move table
            logger.debug(str(threading.get_ident()) + ": AutoMoveTimerThread sent to sleep for interval: " + str(self.interval))
            time.sleep(self.interval)
            logger.debug(str(threading.get_ident()) + ": AutoMoveTimerThread woke up")
            # check if the timer has been cancelled in the meantime - if so, silently die
            if self.event.is_set():
                logger.debug(str(threading.get_ident()) + ": AutoMoveTimerThread stopped")
                break

            # when the timer wakes up, move the table into the alternate position
            next_pos = self.act_sequence[next_move_action]
            # x can be like p1, c87, i38.
            match next_pos[0:1]:
                case "p":
                    # "p" position
                    logger.debug(str(threading.get_ident()) + ": Moving desk to position: " + next_pos)
                    a = on_click_position(int(next_pos[1:]), self.bekant_url)
                    # execute returned function
                    a()
                case "c":
                    # "c" positions
                    logger.debug(str(threading.get_ident()) + ": Moving desk to height (cm): " + next_pos)
                    a = on_click_height(cm_to_raw(int(next_pos[1:])), self.bekant_url)
                    # execute returned function
                    a()
                case "i":
                    # "i" positions
                    logger.debug(str(threading.get_ident()) + ": Moving desk to height (inch): " + next_pos)
                    a = on_click_height(inch_to_raw(int(next_pos[1:])), self.bekant_url)
                    # execute returned function
                    a()

            # move pointer to next element or to the beginning, if this was the last action in the list
            if next_move_action == (len(self.act_sequence) - 1):
                next_move_action = 0
            else:
                next_move_action += 1


def move_table(bekant_url):
    requests.post(bekant_url)
    logger.info(str(threading.get_ident()) + ": Moved desk: " + bekant_url)


def open_in_browser(bekant_url):
    webbrowser.open(bekant_url)
    logger.info(str(threading.get_ident()) + ": Opened in browser: " + bekant_url)


def on_click_position(pos, bekant_url):

    def realfunction():
        logger.info(str(threading.get_ident()) + ": Moving desk to position: " + str(pos))
        move_table(bekant_url + "/button/desk_position_" + str(pos) + "/press")
    return realfunction


def on_click_height(height, bekant_url):

    def realfunction():
        logger.info(str(threading.get_ident()) + ": Moving desk to height: " + str(height))
        move_table(bekant_url + "/number/megadesk_height_raw/set?value=" + str(height))
    return realfunction


# Note: Megadesk does not allow relative movements smaller than 138 raw
# Seems to be a result from the reverse engineering, so we do not acutally know why this is
def on_click_relative_up_height(rel_height, bekant_url):

    def realfunction():
        logger.info(str(threading.get_ident()) + ": Moving desk up relative height: " + str(rel_height))
        move_table(bekant_url + "/number/megadesk_relative_height_up_raw/set?value=" + str(rel_height))
    return realfunction

def on_click_relative_down_height(rel_height, bekant_url):

    def realfunction():
        logger.info(str(threading.get_ident()) + ": Moving desk down relative height: " + str(rel_height))
        move_table(bekant_url + "/number/megadesk_relative_height_down_raw/set?value=" + str(rel_height))
    return realfunction


def on_click_interval(item_name, interv, act_sequence, bekant_url, menuitems_checked_state):

    def realfunction():
        global auto_move_timer
        logger.debug(str(threading.get_ident()) + ": on_click_interval: " + str(interv))
        # global auto_position_change_submenu_index

        # setting the selected checkmark to the selects submenu item in the Auto Position Change submenu
        # Needs to be done via shared variable, as there is no setter methode on the MenuItem object
        # The MenuItems in the submenu list have the same order as the shared variable List auto_position_change_submenu_index
        # Getting the right index by resolving the clicked menuitem's index position in the menuitemlist
        menuitems_checked_state[item_name] = MenuItem.checked
        for key in menuitems_checked_state:
            if key is not item_name:
                menuitems_checked_state[key] = not MenuItem.checked
        logger.debug(str(threading.get_ident()) + ": " + str(menuitems_checked_state))

        systray_icon.update_menu()

        # check if a timer currently is running and if yes, stop it
        # remark: If the user is clicking the same interval that is already running, the interval starts again from
        # the beginning, meaning we have to stop any running timer no matter what
        if auto_move_timer is not None:
            logger.debug(str(threading.get_ident()) + ": Stopping Auto Position Change Timer Thread")
            # set the notification event for stopping a running thread to true
            auto_move_timer.event.set()
            auto_move_timer = None
            systray_icon.icon = image_default

        # now, if the interval equals 0, it means, no timer should be set (off)
        # Since a potentially running autoMoveTimer has already been stopped above, nothing more is left to do
        if interv == 0:
            logger.info(str(threading.get_ident()) + ": Auto Position Change disabled (off)")
            # Notifications are not available on every plattform/backend, so check availability
            if systray_icon.HAS_NOTIFICATION:
                systray_icon.notify('Auto Position Change stopped.', "Megaconnect")

        # Set a new autoMoveTimer with the given interval
        else:
            # create a shared event
            event = Event()
            auto_move_timer = AutoMoveTimerThread(interv, act_sequence, event, bekant_url)
            auto_move_timer.daemon = True
            auto_move_timer.start()
            systray_icon.icon = image_alternate
            # Notifications are not available on every plattform/backend, so check availability
            if systray_icon.HAS_NOTIFICATION:
                systray_icon.notify('Auto Position Change started.', "Megaconnect")

    return realfunction


def clicked_esphome():
    global url
    logger.info(str(threading.get_ident()) + ": Opening Megadesk ESPHome Web Interface ")
    webbrowser.open(url)


def clicked_toggle_audio():
    global url
    logger.info(str(threading.get_ident()) + ": Toggle Audio")
    move_table(url + "/button/toggle_audio_feedback/press")


def clicked_homepage():
    logger.info(str(threading.get_ident()) + ": Opening Megadesk Homepage")
    open_in_browser("https://github.com/gcormier/megadesk")


# noinspection SpellCheckingInspection
def clicked_update():
    logger.info(str(threading.get_ident()) + ": Opening Megaconnect Update-Page")
    open_in_browser("https://github.com/gcormier/megaconnect")


def clicked_exit():
    logger.info(str(threading.get_ident()) + ": Exiting application")
    systray_icon.stop()


def inch_to_raw(inch):
    return int((((inch - 23) * (6914 - 299)) / (47 - 23)) + 299)


def cm_to_raw(cm):
    return int((((cm - 58.42) * (6640 - 299)) / (119.38 - 58.42)) + 299)



# load configuration file
config_data = configparser.ConfigParser()
if os.path.isfile("megaconnect.conf"):
    try:
        config_data.read("megaconnect.conf")
    except configparser.DuplicateOptionError as err:
        sys.exit("Fatal Error: Duplicate configuration item detected: " + str(err))
else:
    sys.exit("Fatal Error: Missing Configuration File './megaconnect.conf/'")

log_level = logging.CRITICAL
logging_conf = config_data["logging"]
if 'loglevel' in logging_conf:
    match logging_conf["loglevel"]:
        case "INFO":
            log_level = logging.INFO
        case "DEBUG":
            log_level = logging.DEBUG

# configure the log to report all messages
logging.basicConfig(filename='megaconnect.log', format='%(asctime)s %(levelname)s:%(message)s', level=log_level)
logger = logging.getLogger()
logger.info("Configuration file loaded")

# global value to hold the AutoMoveTimer thread
auto_move_timer = None

# load images for the systray icon
if os.path.isfile("./icon_default.jpg"):
    image_default = PIL.Image.open("icon_default.jpg")
else:
    logger.error(str(threading.get_ident()) + ": Fatal Error: Missing Systray Icon './icon_default.jpg/'")
    sys.exit("Fatal Error: Missing Systray Icon './icon_default.jpg/'")
if os.path.isfile("./icon_alternate.jpg"):
    image_alternate = PIL.Image.open("icon_alternate.jpg")
else:
    logger.error(str(threading.get_ident()) + ": Fatal Error: Missing Systray Icon './icon_alternate.jpg/'")
    sys.exit("Fatal Error: Missing Systray Icon './icon_alternate.jpg/'")

logger.info("Images for icons loaded")

network_conf = config_data["network"]
positions_conf = config_data["positions"]
intervals_conf = config_data["intervals"]
step_conf = config_data["step"]

logger.debug("network data")
if 'url' not in network_conf:
    logger.error(str(threading.get_ident()) + ": Fatal Error: Missing configuration parameter for URL in configuration file")
    sys.exit("Fatal Error: Missing configuration parameter for URL in configuration file")
for network_data in network_conf:
    url = network_conf.get(network_data).strip()
    logger.debug(f"{network_data} = {network_conf.get(network_data)}")

    if not validators.url(url, public=False):
        logger.error(str(threading.get_ident()) + ": Fatal Error: Invalid value for URL in configuration file: " + url)
        sys.exit("Fatal Error: Invalid value for URL in configuration file: " + url)

# create Menu and MenuItems from configuration
if len(positions_conf) < 2:
    logger.error(str(threading.get_ident()) + ": Fatal Error: Missing or incomplete configuration parameter for "
                                              "[positions] in configuration file. At least two positions are needed.")
    sys.exit("Fatal Error: Missing or incomplete configuration parameter for [positions] in configuration file. "
             "At least two positions are needed.")

menuItems = []

# action_sequence is a list with at least two position intervals, which the AutoMove is using to alternate
# the positioning
action_sequence = []

logger.debug("positions data")
# Regex for ranges p[2-99],c[59-118],i[23-47]
# regex_p = r"((p)([2-9]|[1-9][0-9]))"
# regex_c = r"((c)((59)|[6-9][0-9]|10[0-9]|11[0-8]))"
# regex_i = r"((i)((2)[3-9]|3[0-9]|4[0-7]))"
regex_all = r"((p)([2-9]|[1-9][0-9]))|((c)((59)|[6-9][0-9]|10[0-9]|11[0-8]))|((i)((2)[3-9]|3[0-9]|4[0-7]))"

# Add fix positions for up and down (relative movement to current position)
if 'step' not in step_conf:
    logger.error(str(threading.get_ident()) + ": Fatal Error: Missing configuration parameter for step in configuration file")
    sys.exit("Fatal Error: Missing configuration parameter for step in configuration file")
step = int(step_conf["step"])
if step < 138:
    step = 138
    logger.info(str(threading.get_ident()) + ": Invalid value for step, adjusting to 138")
if step > 6640:
    step = 6640
    logger.info(str(threading.get_ident()) + ": Invalid value for step, adjusting to 6640")

menuItems.append(MenuItem("Step up", on_click_relative_up_height(step, url)))
menuItems.append(MenuItem("Step down", on_click_relative_down_height(step, url)))
menuItems.append(Menu.SEPARATOR)
logger.info(str(threading.get_ident()) + ": Step up and step down added to Menu")

for positions_data in positions_conf:
    # configuration items need to be unique
    logger.debug(f"{positions_data}={positions_conf.get(positions_data)}")
    try:
        # check if it's a valid position (via regex)
        # check what type the position if of (via regex group and substring)
        # get the values and create the related menuItems
        x = (re.search(regex_all, positions_data)).group(0)
        match x[0:1]:
            case "p":
                # MenuItem for "p" positions
                menuItems.append(MenuItem(positions_conf.get(positions_data), on_click_position(int(positions_data[1:]), url)))
                action_sequence.append(str(positions_data))
                logger.info(str(threading.get_ident()) + ": Position added: " + x)
            case "c":
                # MenuItem for "c" positions
                menuItems.append(MenuItem(positions_conf.get(positions_data), on_click_height(cm_to_raw(int(positions_data[1:])), url)))
                action_sequence.append(str(positions_data))
                logger.info(str(threading.get_ident()) + ": Position added: " + x)
            case "i":
                # MenuItem for "i" positions
                menuItems.append(MenuItem(positions_conf.get(positions_data), on_click_height(inch_to_raw(int(positions_data[1:])), url)))
                action_sequence.append(str(positions_data))
                logger.info(str(threading.get_ident()) + ": Position added: " + x)
            case _:
                logger.error(str(threading.get_ident()) + ": Fatal Error: Invalid configuration parameter for [positions] in configuration file: " + positions_data)
                sys.exit("Fatal Error: Invalid configuration parameter for [positions] in configuration file: " + positions_data)

    except ValueError:
        logger.error(str(threading.get_ident()) + ": Fatal Error: Invalid configuration parameter for "
                                                  "[positions] in configuration file: " + positions_data)
        sys.exit("Fatal Error: Invalid configuration parameter for [positions] in configuration file: "
                 + positions_data)

menuItems.append(Menu.SEPARATOR)

menu_items_checked_state = {}
menu_intervals = []
interval_menu_counter = 0
for intervals_data in intervals_conf:
    logger.debug(f"{intervals_data}={intervals_conf.get(intervals_data)}")
    tokens = (intervals_conf.get(intervals_data)).split(":")
    name = tokens[-1]
    tokens.pop()
    menu_items_checked_state[name] = not MenuItem.checked
    menu_intervals.append(MenuItem(name, on_click_interval(name, int(intervals_data), tokens, url, menu_items_checked_state),
                                   default=False, checked=lambda MenuItem: menu_items_checked_state[MenuItem.text]))

    logger.info(str(threading.get_ident()) + ": Interval added: " + intervals_data)
    interval_menu_counter += 1

# create the "off" item
menu_items_checked_state["off"] = MenuItem.checked
menu_intervals.append(MenuItem("off", on_click_interval("off", 0, action_sequence, url, menu_items_checked_state), default=False,
                               checked=lambda MenuItem: menu_items_checked_state[MenuItem.text]))

menuItems.append(MenuItem("Auto Position Change", Menu(lambda: menu_intervals)))
menuItems.append(Menu.SEPARATOR)
menuItems.append(MenuItem("Toggle Audio Feedback", clicked_toggle_audio))
menuItems.append(MenuItem("Megadesk ESPHome Web Interface", clicked_esphome))
menuItems.append(Menu.SEPARATOR)
menuItems.append(MenuItem("Check for Update", clicked_update))
menuItems.append(MenuItem("Megadesk Website", clicked_homepage))
menuItems.append(Menu.SEPARATOR)
menuItems.append(MenuItem("Exit", clicked_exit))

# create systray icon and run the application
systray_icon = Icon("Megadesk remote control", image_default, menu=menuItems)
systray_icon.run()

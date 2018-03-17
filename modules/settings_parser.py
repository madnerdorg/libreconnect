# Arguments parsing
import argparse
import os
import ConfigParser
import sys
def get():
    """ Get arguments list
    
    Returns:
        [args] -- an array of settings
    """

    parser = argparse.ArgumentParser(
        description="Transform a serial port into a websocket")
    parser.add_argument("--serial", default="", help="Serial port (only for connector)")
    parser.add_argument("--serial_scan_interval", default=1, help="Scan usb devices each X seconds")
    parser.add_argument("--serial_retry", default=3, help="Number of times a devices is tested")

    parser.add_argument("--local", default=False, action="store_true",
                        help="Websockets will only be available on the current machine")

    parser.add_argument("--port", default=40000,
                        help="(connector): Websocket port, (usb_scanner):(first port for unknown devices)")
    parser.add_argument("--ssl", default=False, action="store_true",
                        help="Use SSL certificates to encrypt communication")

    parser.add_argument("--power_commands", default=False, action="store_true",
                        help="Add reboot/poweroff commands (@reboot/@poweroff)")

    parser.add_argument("--password", default=False,
                        help="Password for the websocket")
    parser.add_argument("--ip_ban_duration", default=0,
                        help="Seconds before a banned IP is unbanned")
    parser.add_argument("--ip_ban_retry", default=10, 
                        help="Number of wrong password before IP is banned")

    parser.add_argument("--unknown_baudrate", default="9600",
                        help="Baudrate for unknown devices")
    parser.add_argument("--firmata_baudrate", default="57600",
                        help="Baudrate for firmata devices")
    parser.add_argument("--mysensors_baudrate", default="38400",
                        help="Baudrate for mysensors devices")
    parser.add_argument("--libreconnect_baudrate", default="115200",
                        help="Baudrate for libreconnect")

    parser.add_argument("--ssl_certs", default="certs/",
                        help="folders where SSL certificates are")

    parser.add_argument("--settings_file", default="settings/libreconnect.ini",
                        help="Setting file location")
    parser.add_argument("--debug", default=False, action="store_true",
                        help="Debug Mode")

    parser.add_argument("--libreconnect", default=True, action="store_true", 
                        help="Connect libreconnect devices")
    parser.add_argument("--firmata", default=True, action="store_true",
                        help="Connect firmata devices")
    parser.add_argument("--mysensors", default=True, action="store_true",                    
                        help="Connect mysensors devices")
    parser.add_argument("--unknown", default=True, action="store_true",
                        help="Connect unrecognized serial port at unknown baudrate")
    args = vars(parser.parse_args())
    if args["debug"]:
        print("Arguments -------------")
        print(args)
    return args

def get_from_file(args_cmd):
    """ Get arguments from a INI Configuration File
    
    Arguments:
        args {[string]} -- An array previously parsed from command line
    
    Returns:
        [args, config file] -- Returns list of arguments and if a config file was used as a boolean 
    """

    if os.path.isfile(args_cmd["settings_file"]):
        config_file = True
        settings = ConfigParser.ConfigParser()
        settings.read(args_cmd["settings_file"])
        for name,arg in args_cmd.items():
            try:
                args_cmd[name] = settings.get("settings",name)
            except:
                pass
        if args_cmd["debug"]:
            print("Configuration File -------------")
            print(args_cmd)
    return args_cmd,config_file

def get_connector():
    """ Get connector for windows or linux, if a python version exists use it instead 
    
    Returns:
        [string] -- filename of the connector
    """

    # Check if python file existed, if not default to compiled version
    if os.path.exists("connector.py"):
        connector_software = "python connector.py"
    else:
        if sys.platform == "win32":
            connector_software = "connector.exe"
        else:
            connector_software = "./connector"
    return connector_software

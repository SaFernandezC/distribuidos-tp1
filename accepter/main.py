# #!/usr/bin/env python3

# from configparser import ConfigParser
# from server import Server
# import logging
# import os


# def initialize_config():
#     """ Parse env variables or config file to find program config params

#     Function that search and parse program configuration parameters in the
#     program environment variables first and the in a config file. 
#     If at least one of the config parameters is not found a KeyError exception 
#     is thrown. If a parameter could not be parsed, a ValueError is thrown. 
#     If parsing succeeded, the function returns a ConfigParser object 
#     with config parameters
#     """

#     config = ConfigParser(os.environ)
#     # If config.ini does not exists original config object is not modified
#     config.read("config.ini")

#     config_params = {}
#     try:
#         config_params["port"] = int(os.getenv('SERVER_PORT', config["DEFAULT"]["SERVER_PORT"]))
#         config_params["listen_backlog"] = int(os.getenv('SERVER_LISTEN_BACKLOG', config["DEFAULT"]["SERVER_LISTEN_BACKLOG"]))
#         config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
#     except KeyError as e:
#         raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
#     except ValueError as e:
#         raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

#     return config_params


# def main():
#     config_params = initialize_config()
#     logging_level = config_params["logging_level"]
#     port = config_params["port"]
#     listen_backlog = config_params["listen_backlog"]

#     initialize_log(logging_level)

#     # Log config parameters at the beginning of the program to verify the configuration
#     # of the component
#     logging.debug(f"action: config | result: success | port: {port} | "
#                   f"listen_backlog: {listen_backlog} | logging_level: {logging_level}")

#     # Initialize server and start server loop
#     server = Server(port, listen_backlog)
#     server.run()

# def initialize_log(logging_level):
#     """
#     Python custom logging initialization

#     Current timestamp is added to be able to identify in docker
#     compose logs the date when the log has arrived
#     """
#     logging.basicConfig(
#         format='%(asctime)s %(levelname)-8s %(message)s',
#         level=logging_level,
#         datefmt='%Y-%m-%d %H:%M:%S',
#     )


import pika

def main():

    line1 = "2014-04-01,0.01,2.99,88.53,100.53,10.08,-1.54,-3.33,-3.31,2.44,-7.64,-1.57,3.21,2.21,5.11,3.25,8.32,5.46,6.62,4.21,2014"
    line2 = "2014-04-02,0.06,3.63,89.75,100.03,8.66,0.41,-0.73,-0.72,3.75,-4.91,0.83,3.16,3.55,6.21,3.12,9.37,6.67,7.69,4.72,2014"
    line3 = "2014-04-03,0.59,2.57,85.51,100.65,7.1,-2.89,-5.25,-5.22,0.4,-6.7,-3.14,2.41,1.65,4.24,2.4,6.65,4.06,5.18,3.44,2014"
    line4 = "2014-04-04,9.05,3.25,91.28,99.94,11.31,-0.74,-2.67,-2.65,3.81,-7.5,-0.96,5.04,4.1,6.08,3.42,11.12,7.51,7.85,5.45,2014"
    line5 = "2014-04-05,2.05,3.73,86.95,99.02,6.58,1.26,-0.55,-0.54,3.93,-2.65,1.49,2.48,2.74,9.79,6.04,12.27,8.78,10.77,7.51,2014"



    return 0

if __name__ == "__main__":
    main()
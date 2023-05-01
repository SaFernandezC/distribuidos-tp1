import json
from common.queue import Queue
from configparser import ConfigParser
from server import Server
import logging
import os
import time


def initialize_config():
    config = ConfigParser(os.environ)
    config.read("config.ini")

    config_params = {}
    try:
        config_params["port"] = int(os.getenv('SERVER_PORT', config["DEFAULT"]["SERVER_PORT"]))
        config_params["listen_backlog"] = int(os.getenv('SERVER_LISTEN_BACKLOG', config["DEFAULT"]["SERVER_LISTEN_BACKLOG"]))
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["trip_parsers"] = int(os.getenv('TRIP_PARSERS', config["DEFAULT"]["TRIP_PARSERS"]))
        config_params["weather_parsers"] = int(os.getenv('WEATHER_PARSERS', config["DEFAULT"]["WEATHER_PARSERS"]))
        config_params["station_parsers"] = int(os.getenv('STATION_PARSERS', config["DEFAULT"]["STATION_PARSERS"]))
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

def main():
    config_params = initialize_config()
    logging_level = config_params["logging_level"]
    port = config_params["port"]
    listen_backlog = config_params["listen_backlog"]
    trip_parsers = config_params["trip_parsers"]
    weather_parsers = config_params["weather_parsers"]
    station_parsers = config_params["station_parsers"]

    initialize_log(logging_level)

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.info(f"action: config | result: success | port: {port} | "
                  f"listen_backlog: {listen_backlog} | logging_level: {logging_level} |"
                  f"trip_parser: {trip_parsers} | weather_parsers: {weather_parsers}, station_parsers: {station_parsers}")

    # Initialize server and start server loop
    server = Server(port, listen_backlog, trip_parsers, weather_parsers, station_parsers)
    server.run()

    # time.sleep(5)
    # queue = Queue(exchange_name='weathers', exchange_type='fanout')
    # trips_queue = Queue(queue_name='trips_1')

    # finished = False
    # i = 0
    # try:
    #     with open("./weather.csv") as file:
    #         while not finished:
    #             line = file.readline().strip()

    #             if i == 0:
    #                 i += 1
    #                 continue
                    
    #             if not line:
    #                 finished = True
    #             else:
    #                 parsed = line.split(',')
    #                 weather = {"city": "montreal", "date":parsed[0], "prectot": parsed[1], "yearid": parsed[-1]}
    #                 # print(weather)
    #                 queue.send(body=json.dumps(weather))
        
    #     queue.send(body=json.dumps({"eof":1}))
        
    #     trip = {"city": "montreal", "start_date":'2016-08-15', "duration_sec": '10'}
    #     trips_queue.send(body=json.dumps(trip))

    #     trip = {"city": "montreal", "start_date":'2016-08-15', "duration_sec": '5'}
    #     trips_queue.send(body=json.dumps(trip))

    #     trip = {"city": "montreal", "start_date":'2016-10-20', "duration_sec": '15'}
    #     trips_queue.send(body=json.dumps(trip))

    #     trip = {"city": "toronto", "start_date":'2016-10-21', "duration_sec": '15'}
    #     trips_queue.send(body=json.dumps(trip))

    #     trip = {"city": "montreal", "start_date":'2016-15-21', "duration_sec": '15'}
    #     trips_queue.send(body=json.dumps(trip))
    #     # trips_queue.send(body=json.dumps({"eof":1}))

    #     return 0
    # except Exception as e:
    #     logging.error("action: apuestas enviadas | result: fail | error: {}".format(e)) 


if __name__ == '__main__':
    main()
import json
from common.queue import Queue
from configparser import ConfigParser
import logging
import os
import functools
from utils import send, handle_eof, parse_weathers, parse_trips, parse_stations


def initialize_config():
    config = ConfigParser(os.environ)
    config.read("config.ini")

    config_params = {}
    try:
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["routing_key"] = os.getenv('ROUTING_KEY', config["DEFAULT"]["ROUTING_KEY"])
        config_params["input_queue"] = os.getenv('INPUT_QUEUE', config["DEFAULT"]["INPUT_QUEUE"])
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


# args[3] = eof_manager
def callback(ch, method, properties, body, args):
    batch = json.loads(body.decode())
    if "eof" in batch:
        handle_eof(batch, args[0], args[1], args[2], args[3])
        args[4].stop_consuming()
        print("RECIBO EOF ---> DEJO DE ESCUCHAR")
    else:

        if batch["type"] == "weathers":
            send(args[0], batch['city'], batch['data'], parse_weathers)
        elif batch["type"] == "trips":
            send(args[1], batch['city'], batch['data'], parse_trips)
        else: # Stations
            send(args[2], batch['city'], batch['data'], parse_stations)

def main():
    config_params = initialize_config()
    logging_level = config_params["logging_level"]
    routing_key = config_params["routing_key"]
    input_queue = config_params["input_queue"]

    initialize_log(logging_level)
    logging.info(f"action: config | result: success | logging_level: {logging_level}")

    # input_queue = Queue(queue_name="raw_data")
    input_queue = Queue(exchange_name='raw_data', exchange_type='direct', bind=True, routing_key=routing_key, queue_name=input_queue)

    weathers_queue = Queue(exchange_name='weathers', exchange_type='fanout')
    trips_queue = Queue(exchange_name="trips", exchange_type='fanout')
    stations_queue = Queue(exchange_name="stations", exchange_type='fanout')
    eof_manager = Queue(queue_name="eof_manager")


    on_message_callback = functools.partial(callback, args=(weathers_queue, trips_queue, stations_queue, eof_manager, input_queue))
    input_queue.recv(callback=on_message_callback)
    
if __name__ == '__main__':
    main()
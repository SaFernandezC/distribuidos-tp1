import ujson as json
from common.queue import Queue
from configparser import ConfigParser
import logging
import os
import functools
from utils import send, handle_eof, parse_weathers, parse_trips, parse_stations
import time
import pika


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


def callback(ch, method, properties, body, args):
    batch = json.loads(body.decode())
    if "eof" in batch:
        print(f"{time.asctime(time.localtime())} RECIBO EOF ---> DEJO DE ESCUCHAR")
        handle_eof(batch, args[0], args[1], args[2], args[3], args[4], ch)
        ch.stop_consuming()
    else:
        if batch["type"] == "weathers":
            send(args[0], batch['city'], batch['data'], parse_weathers, ch)
        elif batch["type"] == "trips":
            send(args[1], batch['city'], batch['data'], parse_trips, ch)
        else: # Stations
            send(args[2], batch['city'], batch['data'], parse_stations, ch)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    config_params = initialize_config()
    logging_level = config_params["logging_level"]
    routing_key = config_params["routing_key"]
    input_queue = config_params["input_queue"]

    initialize_log(logging_level)
    logging.info(f"action: config | result: success | logging_level: {logging_level}")

    # input_queue = Queue(queue_name=routing_key)
    # # input_queue = Queue(exchange_name='raw_data', exchange_type='direct', bind=True, routing_key=routing_key, queue_name=input_queue)

    # weathers_queue = Queue(exchange_name='weathers', exchange_type='fanout')
    # trips_queue = Queue(exchange_name="trips", exchange_type='fanout')
    # stations_queue = Queue(exchange_name="stations", exchange_type='fanout')

    # eof_manager = Queue(queue_name="eof_manager")

    connection = pika.BlockingConnection(
                                pika.ConnectionParameters(host='rabbitmq', heartbeat=1200))
    channel = connection.channel()

    result = channel.queue_declare(queue=routing_key, durable=True)
    input_queue = result.method.queue

    result = channel.queue_declare(queue="eof_manager", durable=True)
    eof_manager = result.method.queue

    channel.exchange_declare(exchange='weathers', exchange_type='fanout')
    channel.exchange_declare(exchange='trips', exchange_type='fanout')
    channel.exchange_declare(exchange='stations', exchange_type='fanout')



    on_message_callback = functools.partial(callback, args=("weathers", "trips", "stations", eof_manager, routing_key))
    # input_queue.recv(callback=on_message_callback, auto_ack=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=input_queue, on_message_callback=on_message_callback)

    channel.start_consuming()

    time.sleep(50)

    # input_queue.close() 
    # weathers_queue.close() 
    # trips_queue.close() 
    # stations_queue.close() 
    # eof_manager.close() 

if __name__ == '__main__':
    main()
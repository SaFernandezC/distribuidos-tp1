import logging
import signal
import multiprocessing
from common.queue import Queue
import json
import time

WORKERS = 3
SEND_WEATHERS = 'W'
SEND_STATIONS = 'S'
SEND_TRIPS = 'T'


def build_weather(item, city):
    item = item.split(',')
    return json.dumps({"city": city, "date": item[0], "prectot": item[1]})

def build_trip(item, city):
    item = item.split(',')
    return json.dumps({"city": city, "date": item[0], "prectot": item[1]})

def send(queue, data, city, builder):
    for item in data:
        queue.send(builder(item, city))

def send_eof(queue, batch):
    queue.send(json.dumps(batch))


def push_data(batchs_queue):
    logging.info(f'Worker: push data')
    weathers_queue = Queue(exchange_name='weathers', exchange_type='fanout')
    trips_queue = Queue(exchange_name='trips', exchange_type='fanout')

    while True:
        batch = batchs_queue.get()
        if "eof" in batch:
            send_eof(weathers_queue, batch)
            continue

        data = batch["data"]
        city = batch["city"]
        if batch["type"] == "weathers":
            send(weathers_queue, data, city, build_weather)


        



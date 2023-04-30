import os
from common.queue import Queue
from dotenv import load_dotenv
import json
import functools
from haversine import haversine

load_dotenv()

INPUT_QUEUE_NAME = os.getenv('INPUT_QUEUE_NAME')
OUTPUT_QUEUE_NAME = os.getenv('OUTPUT_QUEUE_NAME')


def callback_queue1(ch, method, properties, body, args):
    line = json.loads(body.decode())
    if "eof" in line:
        args[0].send(body=body)
        return
    
    distance = haversine((line['start_latitude'], line['start_longitude']), (line['end_latitude'], line['end_longitude']))
    res = {"end_name": line["end_name"], "distance": distance}
    args[0].send(body=json.dumps(res))


def main():

    input_queue = Queue(queue_name=INPUT_QUEUE_NAME)
    output_queue = Queue(queue_name=OUTPUT_QUEUE_NAME)

    on_message_callback = functools.partial(callback_queue1, args=(output_queue, ))
    input_queue.recv(callback=on_message_callback)


if __name__ == "__main__":
    main()
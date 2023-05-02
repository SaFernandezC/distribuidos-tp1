import os
from common.queue import Queue
from dotenv import load_dotenv
import json
import functools

load_dotenv()

INPUT_QUEUE_NAME = os.getenv('INPUT_QUEUE_NAME', '')
OUTPUT_QUEUE_NAME = os.getenv('OUTPUT_QUEUE_NAME', '')
QTY_OF_QUERIES = int(os.getenv('QTY_OF_QUERIES', ''))

data = {}

def callback(ch, method, properties, body, args):
    line = json.loads(body.decode())
    data[line["query"]] = line["results"]

    if len(data) == QTY_OF_QUERIES:
        args[0].send(body=json.dumps(data))
        print("Resultado: ", data)

def main():
    input_queue = Queue(queue_name=INPUT_QUEUE_NAME)
    output_queue = Queue(queue_name=OUTPUT_QUEUE_NAME)

    on_message_callback = functools.partial(callback, args=(output_queue,))
    input_queue.recv(callback=on_message_callback)


if __name__ == "__main__":
    main()
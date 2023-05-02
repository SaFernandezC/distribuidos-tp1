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
        # args[0].send(body=body) # AGREFAR EOF MANAGER ACA
        ch.stop_consuming()
        args[1].send(body=json.dumps({"type":"work_queue", "queue": OUTPUT_QUEUE_NAME}))
    else:
        distance = haversine((line['start_latitude'], line['start_longitude']), (line['end_latitude'], line['end_longitude']))
        res = {"end_name": line["end_name"], "distance": distance}
        args[0].send(body=json.dumps(res))
    # ch.basic_ack(delivery_tag=method.delivery_tag)

def main():

    input_queue = Queue(queue_name=INPUT_QUEUE_NAME)
    output_queue = Queue(queue_name=OUTPUT_QUEUE_NAME)
    eof_manager = Queue(queue_name="eof_manager")

    on_message_callback = functools.partial(callback_queue1, args=(output_queue, eof_manager))
    input_queue.recv(callback=on_message_callback, auto_ack=True)


if __name__ == "__main__":
    main()
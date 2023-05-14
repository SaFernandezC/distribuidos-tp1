import os
from common.queue import Queue
from dotenv import load_dotenv
import ujson as json
import functools
from haversine import haversine
import time
import pika

load_dotenv()

INPUT_QUEUE_NAME = os.getenv('INPUT_QUEUE_NAME')
OUTPUT_QUEUE_NAME = os.getenv('OUTPUT_QUEUE_NAME')


def callback(ch, method, properties, body, args):
    line = json.loads(body.decode())
    if "eof" in line:
        # args[0].send(body=body) # AGREFAR EOF MANAGER ACA
        ch.stop_consuming()
        # args[1].send(body=json.dumps({"type":"work_queue", "queue": OUTPUT_QUEUE_NAME}))
        ch.basic_publish(exchange='',
                            routing_key='eof_manager',
                            body=json.dumps({"type":"work_queue", "queue": OUTPUT_QUEUE_NAME}))
    else:
        distance = haversine((line['start_latitude'], line['start_longitude']), (line['end_latitude'], line['end_longitude']))
        res = {"end_name": line["end_name"], "distance": distance}
        # args[0].send(body=json.dumps(res))
        ch.basic_publish(exchange='',
                            routing_key=OUTPUT_QUEUE_NAME,
                            body=json.dumps(res))

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():

    # input_queue = Queue(queue_name=INPUT_QUEUE_NAME)
    # output_queue = Queue(queue_name=OUTPUT_QUEUE_NAME)
    # eof_manager = Queue(queue_name="eof_manager")

    # on_message_callback = functools.partial(callback, args=(output_queue, eof_manager))
    # input_queue.recv(callback=on_message_callback, auto_ack=False)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', heartbeat=1200))
    channel = connection.channel()

    result = channel.queue_declare(queue="eof_manager", durable=True)
    eof_manager = result.method.queue

    result = channel.queue_declare(queue=INPUT_QUEUE_NAME, durable=True)
    input_queue = result.method.queue

    result = channel.queue_declare(queue=OUTPUT_QUEUE_NAME, durable=True)
    output_queue = result.method.queue


    on_message_callback = functools.partial(callback, args=("output_queue", input_queue, eof_manager))
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=input_queue, on_message_callback=on_message_callback)
    channel.start_consuming()

    time.sleep(50)

if __name__ == "__main__":
    main()
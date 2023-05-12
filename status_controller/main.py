import os
from common.queue import Queue
from dotenv import load_dotenv
import json
import functools
import pika 

load_dotenv()

INPUT_QUEUE_NAME = os.getenv('INPUT_QUEUE_NAME', '')
OUTPUT_QUEUE_NAME = os.getenv('OUTPUT_QUEUE_NAME', '')
QTY_OF_QUERIES = int(os.getenv('QTY_OF_QUERIES', ''))

data = {}

def callback(ch, method, properties, body, args):
    line = json.loads(body.decode())
    data[line["query"]] = line["results"]
    print(line)

    if len(data) == QTY_OF_QUERIES:
        # args[0].send(body=json.dumps(data))
        ch.basic_publish(exchange='',
                      routing_key=OUTPUT_QUEUE_NAME,
                      body=json.dumps(data))
        print("Resultado: ", data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    # input_queue = Queue(queue_name=INPUT_QUEUE_NAME)
    # output_queue = Queue(queue_name=OUTPUT_QUEUE_NAME)

    # on_message_callback = functools.partial(callback, args=(output_queue,))
    # input_queue.recv(callback=on_message_callback)

    connection = pika.BlockingConnection(
                                pika.ConnectionParameters(host='rabbitmq', heartbeat=1200))
    channel = connection.channel()

    result = channel.queue_declare(queue=INPUT_QUEUE_NAME, durable=True)
    input_queue = result.method.queue

    result = channel.queue_declare(queue=OUTPUT_QUEUE_NAME, durable=True)
    output_queue = result.method.queue

    on_message_callback = functools.partial(callback, args=(output_queue,))
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=input_queue, on_message_callback=on_message_callback)
    channel.start_consuming()


if __name__ == "__main__":
    main()
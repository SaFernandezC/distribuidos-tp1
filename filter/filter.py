#!/usr/bin/env python3
import pika
import time
from common.queue import Queue

# time.sleep(15)

# connection = pika.BlockingConnection(
#     pika.ConnectionParameters(host='rabbitmq'))

# channel = connection.channel()
# channel.queue_declare(queue='hello', durable=True)

queue = Queue(queue_name='hello')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

print(' [*] Waiting for messages. To exit press CTRL+C')
queue.recv(callback=callback)

# channel.basic_consume(
#     queue='hello', on_message_callback=callback, auto_ack=True)

# print(' [*] Waiting for messages. To exit press CTRL+C')
# channel.start_consuming()
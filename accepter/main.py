#!/usr/bin/env python3
import pika
import time

from common.queue import Queue


def main():
    # time.sleep(15)

    # connection = pika.BlockingConnection(
    #     pika.ConnectionParameters(host='rabbitmq'))
    # channel = connection.channel()

    # channel.queue_declare(queue='hello')

    queue = Queue(queue_name='hello')

    for i in range(100):
        # channel.basic_publish(exchange='', routing_key='hello', body='Hello World {}!'.format(i))
        queue.send(body='Hello World {}!'.format(i), routing_key='hello')
        print(" [x] Sent 'Hello World {}!'".format(i))
        time.sleep(1)

    # connection.close()
    queue.close()


if __name__ == '__main__':
    main()
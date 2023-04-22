import time
import pika

class Queue:
    def __init__(self, queue_name='', exchange_name='', bind=False, conn=None, exchange_type='', routing_key=''):
        # if not conn:
        time.sleep(15)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        self.channel = self.connection.channel()
        # else:
        #     self.connection = conn.connection
        #     self.channel = conn.channel

        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self._declare(bind, exchange_type, routing_key)

    def _declare(self, bind, exchange_type, routing_key):
        if self.queue_name != '':
            self.channel.queue_declare(queue=self.queue_name, durable=True)

        if self.exchange_name != '':
            self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=exchange_type)

        if bind:
            result = self.channel.queue_declare(queue='', exclusive=True)
            self.queue_name = result.method.queue

            if routing_key:
                self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=routing_key)
            else:
                self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name)

    def send(self, body, routing_key=None):
        if routing_key == None:
            routing_key = self.queue_name

        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=routing_key,
            body=body,
            # properties=pika.BasicProperties(delivery_mode=2)
        )

    def recv(self, callback, start_consuming=True):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        if start_consuming:
            self.channel.start_consuming()

    def close(self):
        self.channel.stop_consuming()
        self.connection.close()

    def get_connection(self):
        return self.connection, self.channel
import pika

class WorkQueue():
    def __init__(self, channel, queue_name):
        self.channel = channel
        self.queue = channel.queue_declare(queue=queue_name, durable=True)
        self.queue_name = self.queue.method.queue
        self.user_callback = None

    def receive(self, callback):
        self.user_callback = callback
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._callback, auto_ack=True)

    def _callback(self, ch, method, properties, body):
        self.user_callback(body)
        # ch.basic_ack(delivery_tag=method.delivery_tag)

    def send(self, message):
        self.channel.basic_publish(exchange='',
                      routing_key=self.queue_name,
                      body=message)
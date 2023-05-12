import pika

class WorkQueue():
    def __init__(self, channel, queue_name, callback):
        self.channel = channel
        self.queue = channel.queue_declare(queue=queue_name, durable=True)
        self.queue_name = self.queue.method.queue
        self.callback = callback

    def receive(self, callback):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._callback)

    def _callback(self, ch, method, properties, body):
        self.callback(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send(self, message):
        self.channel.basic_publish(exchange='',
                      routing_key=self.queue_name,
                      body=message)
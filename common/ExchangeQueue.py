import pika

class ExchangeQueue():
    def __init__(self, channel, exchange_name, exchange_type, queue_name=None):
        
        self.channel = channel
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.user_callback = None
        channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)
        self.queue_name = self._declare_queue(exchange_name, queue_name)

    def _declare_queue(self, exchange_name, queue_name):
        if not queue_name:
            result = self.channel.queue_declare(queue='', durable=True)
            queue_name = result.method.queue
        else:
            self.channel.queue_declare(queue=queue_name, durable=True)

        self.channel.queue_bind(exchange=exchange_name, queue=queue_name)
        return queue_name


    def receive(self, callback):
        self.user_callback = callback
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._callback)


    def _callback(self, ch, method, properties, body):
        self.user_callback(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send(self, message):
        self.channel.basic_publish(exchange=self.exchange_name,
                      routing_key='',
                      body=message)
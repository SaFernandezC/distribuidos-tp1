import json

class EofQueue():
    def __init__(self, channel, output_exchange, output_queue, input_queue):
        
        self.channel = channel
        self.output_exchange = output_exchange
        self.output_queue = output_queue
        self.input_queue = input_queue
        self.user_callback = None

        self.queue = channel.queue_declare(queue='eof_manager', durable=True)
        self.queue_name = self.queue.method.queue

        if not output_exchange:
            self.eof_msg = json.dumps({"type":"work_queue", "queue": output_queue})
        else:
            self.eof_msg = json.dumps({"type":"exchange", "exchange": output_exchange})


    def receive(self, callback):
        self.user_callback = callback
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._callback, auto_ack=True)


    def _callback(self, ch, method, properties, body):
        self.user_callback(body)
        # ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_eof(self, msg=None):
        if not msg:
            msg = self.eof_msg
        self.channel.basic_publish(exchange='',
                      routing_key=self.queue_name,
                      body=msg)
        if self.input_queue:
            self.channel.basic_publish(exchange='',
                        routing_key=self.input_queue,
                        body=json.dumps({"eof": True}))
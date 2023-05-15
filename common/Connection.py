import pika
from .WorkQueue import WorkQueue
from .ExchangeQueue import ExchangeQueue
from .EofQueue import EofQueue

class Connection:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', heartbeat=1800))
        self.channel = self.connection.channel()

    def Consumer(self, queue_name):
        return WorkQueue(self.channel, queue_name)

    def Producer(self, queue_name):
        return WorkQueue(self.channel, queue_name)

    def Publisher(self, exchange_name, exchange_type):
        return ExchangeQueue("pub", self.channel, exchange_name, exchange_type)

    def Subscriber(self, exchange_name, exchange_type, queue_name=None):
        return ExchangeQueue("sub", self.channel, exchange_name, exchange_type, queue_name)

    def EofProducer(self, output_exchange, output_queue, input_queue):
        return EofQueue(self.channel, output_exchange, output_queue, input_queue)
    
    # def EofConsumer(self, output_exchange, output_queue, input_queue):
    #     return EofQueue(self.channel, output_exchange, output_queue, input_queue)

    def start_consuming(self):
        self.channel.start_consuming()

    def stop_consuming(self):
        self.channel.stop_consuming()

    def close(self):
        self.channel.close()
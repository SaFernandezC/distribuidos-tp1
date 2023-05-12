import pika
from WorkQueue import WorkQueue

class Connection:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', heartbeat=1800))
        self.channel = self.connection.channel()
    
    def queue(self, queue_name=None, exchange_name=None, echange_type=None, callback=None):
        if queue_name != None and callback != None:
            return WorkQueue(self.channel, queue_name, callback)
        else:
            return 0

    def eof_queue(self, output_queue_name, output_exchange_name):
        # Con esos datos ya se que queue crear y que mensaje mandar
        return 0

    def Consumer(self, queue_name, callback):
        return WorkQueue(self.channel, queue_name, callback)

    def Producer(self):
        return 0

    def Publisher(self):
        return 0

    def Subscriber(self):
        return 0

    def start_consuming(self):
        self.channel.start_consuming()

    def stop_consuming(self):
        self.channel.stop_consuming()
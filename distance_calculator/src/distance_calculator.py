from common.Connection import Connection
import ujson as json
from haversine import haversine

class DistanceCalculator:

    def __init__(self, input_queue_name, output_queue_name):

        self.connection = Connection()
        self.input_queue = self.connection.Consumer(input_queue_name)
        self.eof_manager = self.connection.EofProducer(None, output_queue_name, input_queue_name)
        self.output_queue = self.connection.Producer(output_queue_name)
    
    def _callback(self, body):
        line = json.loads(body.decode())
        if "eof" in line:
            self.connection.stop_consuming()
            self.eof_manager.send_eof()
        else:
            distance = haversine((line['start_latitude'], line['start_longitude']), (line['end_latitude'], line['end_longitude']))
            res = {"end_name": line["end_name"], "distance": distance}
            res = json.dumps(res)
            self.output_queue.send(res)

    
    def run(self):
        self.input_queue.receive(self._callback)
        self.connection.start_consuming()
        self.connection.close()
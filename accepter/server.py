import logging
import signal
from socket_wrapper import Socket
from protocol import Protocol
import multiprocessing
from common.queue import Queue
from utils import push_data

WORKERS = 1
SEND_WEATHERS = 'W'
SEND_STATIONS = 'S'
SEND_TRIPS = 'T'
FINISH = 'F'
SEND_DATA = 'D'

class Server:
    def __init__(self, port, listen_backlog):
        self._server_socket = Socket()
        self._server_socket.bind('', port)
        self._server_socket.listen(listen_backlog)
        
        self.is_alive = True
        signal.signal(signal.SIGTERM, self._handle_sigterm)

        self.protocol = Protocol()

        self.batchs_queue = multiprocessing.Queue()
        self._workers = [multiprocessing.Process(target=push_data,
                                                 args=(self.batchs_queue,))
                                                 for i in range(WORKERS)]
                                                 
        for worker in self._workers:
            worker.start()
        # self.weathers_queue = Queue(exchange_name='weathers', exchange_type='fanout')
        self.queue = Queue(queue_name="raw_data")


    def recv_weathers(self, client_sock):
        logging.info(f'action: receiving weathers')
        data = self.protocol.recv_weathers(client_sock)
        self.batchs_queue.put(data)
        self.protocol.send_ack(client_sock, True)
    
    def recv_trips(self, client_sock):
        logging.info(f'action: receiving trips')
        data = self.protocol.recv_trips(client_sock)
        self.batchs_queue.put(data)
        self.protocol.send_ack(client_sock, True)

    def recv_data(self, client_sock):
        logging.debug(f'action: receiving data')
        data = self.protocol.recv_data(client_sock)
        self.queue.send(body=data)
        self.protocol.send_ack(client_sock, True)

    def handle_con(self, client_sock):
        while True:
            action = self.protocol.recv_action(client_sock)
            
            if action == SEND_DATA:
                self.recv_data(client_sock)
            elif action == FINISH:
                self.protocol.send_ack(client_sock, True)
                break

    
    def run(self):
        """
        Main process: starts other processes and iterate accepting new clients.
        After accepting a new client pushes it to clients queue
        """
        while self.is_alive:
            client_sock = self.__accept_new_connection()
            if client_sock:
                self.handle_con(client_sock)
            elif self.is_alive:
                self.stop()

    def __accept_new_connection(self):
        """
        Accept new connections
        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """
        logging.info('action: accept_connections | result: in_progress')
        c = self._server_socket.accept()
        addr = c.get_addr()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c

    def _handle_sigterm(self, *args):
        """
        Handles SIGTERM signal
        """
        logging.info('SIGTERM received - Shutting server down')
        self.stop()

    def stop(self):
        """
        Stops the server
        """
        self.is_alive = False
        try:
            self._server_socket.close()
        except OSError as e:
            logging.error("action: stop server | result: fail | error: {}".format(e))
        finally:
            logging.info('Server stopped')  
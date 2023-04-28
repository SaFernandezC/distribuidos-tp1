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


    # def _handle_connection(self, clients_queue, bets_queue):
    #     """
    #     Workers process: Takes clients from clients_queue, receives one bets batch from that
    #     client, pushes that batch to bets_queue then sends ack to client.
    #     If that was NOT the last batch pushes the client back to clients_queue to
    #     repite the process.
    #     Processing is done by batch and not by client.
    #     """
    #     while True:
    #         try:
    #             client_sock = clients_queue.get()
    #             batch = self.protocol.recv_bets(client_sock)
    #             bets, last_batch_received = self.parse_msg(batch)

    #             bets_queue.put((client_sock, bets, last_batch_received))
    #             self.protocol.send_ack(client_sock, True)
                
    #             if not last_batch_received:
    #                 clients_queue.put(client_sock)
    #             else:
    #                 logging.info(f"action: all bets received from agency | result: success | agency: {batch['agency']}")

    #             logging.debug(f"action: batch almacenado | result: success | agency: {batch['agency']} | cantidad apuestas: {len(batch['data'])}")
    #         except Exception as e:
    #             logging.error("action: handle_connections | result: fail | error: {}".format(e))

    def recv_weathers(self, client_sock):
        logging.info(f'action: receiving weathers')
        data = self.protocol.recv_weathers(client_sock)
        self.batchs_queue.put(data)
        # print(data)

        return 0


    def handle_con(self, client_sock):
        while True:
            # action = self.protocol.recv_action(client_sock)
            
            # if action == SEND_WEATHERS:
            self.recv_weathers(client_sock)

    
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
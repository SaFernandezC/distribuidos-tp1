import logging
import signal
from socket import Socket
# from shared.protocol import Protocol
import multiprocessing

WORKERS = 3

class Server:
    def __init__(self, port, listen_backlog):
        self._server_socket = Socket()
        self._server_socket.bind('', port)
        self._server_socket.listen(listen_backlog)
        
        self.is_alive = True
        signal.signal(signal.SIGTERM, self._handle_sigterm)

        # self.protocol = Protocol()


    # def _handle_connection(self, clients_queue, bets_queue):
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

    def _handle_connection(self, clients_queue, bets_queue):
        while True:
            try:


                # client_sock = clients_queue.get()
                # line = self.protocol.recv_bets(client_sock)
                # bets, last_batch_received = self.parse_msg(batch)

                # bets_queue.put((client_sock, bets, last_batch_received))
                # self.protocol.send_ack(client_sock, True)
                
                # if not last_batch_received:
                #     clients_queue.put(client_sock)
                # else:
                #     logging.info(f"action: all bets received from agency | result: success | agency: {batch['agency']}")

                logging.debug(f"action: batch almacenado | result: success | agency: {batch['agency']} | cantidad apuestas: {len(batch['data'])}")
            except Exception as e:
                logging.error("action: handle_connections | result: fail | error: {}".format(e))

    def run(self):
        while self.is_alive:
            client_sock = self.__accept_new_connection()
            if client_sock:
                self._handle_connection(client_sock)
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
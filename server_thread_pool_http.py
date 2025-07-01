from socket import *
import socket
import time
import sys
import logging
from concurrent.futures import ThreadPoolExecutor
from game_http_server import HttpServer

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv = ""
    while True:
        try:
            data = connection.recv(1024)
            if data:
                d = data.decode()
                rcv = rcv + d
                if rcv.endswith('\r\n\r\n'):
                    hasil = httpserver.proses(rcv)
                    connection.sendall(hasil)
                    connection.close()
                    break
            else:
                break
        except OSError as e:
            break
    connection.close()
    return

def Server(port=8000):
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    my_socket.bind(('0.0.0.0', port))
    my_socket.listen(10)
    logging.warning(f"🚀 Server Game Tunggal berjalan di port {port} 🚀")

    with ThreadPoolExecutor(20) as executor:
        while True:
            connection, client_address = my_socket.accept()
            logging.info(f"Menerima koneksi dari {client_address}")
            p = executor.submit(ProcessTheClient, connection, client_address)
            the_clients.append(p)

def main():
    Server(port=8000)

if __name__=="__main__":
    logging.basicConfig(level=logging.WARNING)
    main()

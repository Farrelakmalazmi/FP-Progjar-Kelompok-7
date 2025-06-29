import socket
import threading
import itertools
import logging
from datetime import datetime

BACKEND_SERVERS = [
    ('127.0.0.1', 8001),
    ('127.0.0.1', 8002),
    ('127.0.0.1', 8003),
]

server_cycler = itertools.cycle(BACKEND_SERVERS)
lock = threading.Lock()

def create_error_response(code, message):
    body = f"<html><body><h1>{code} {message}</h1><p>Load balancer could not connect to a backend server.</p></body></html>".encode('utf-8')
    resp = [
        f"HTTP/1.1 {code} {message}\r\n",
        f"Date: {datetime.now().strftime('%c')}\r\n",
        "Server: LoadBalancer/1.0\r\n",
        f"Content-Length: {len(body)}\r\n",
        "Content-Type: text/html\r\n",
        "Connection: close\r\n",
        "\r\n"
    ]
    return "".join(resp).encode('utf-8')

def handle_request(client_socket):
    with lock:
        backend_server_address = next(server_cycler)
    
    logging.info(f"Meneruskan koneksi ke backend server di {backend_server_address}")

    backend_socket = None
    try:
        request_from_client = b''
        client_socket.settimeout(2) 
        while True:
            try:
                part = client_socket.recv(4096)
                if not part: break
                request_from_client += part
                if b'\r\n\r\n' in request_from_client: break
            except socket.timeout:
                break
        
        if not request_from_client:
            logging.warning("Tidak ada request yang diterima dari client.")
            return

        backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_socket.connect(backend_server_address)

        backend_socket.sendall(request_from_client)

        response_from_backend = b''
        backend_socket.settimeout(2)
        while True:
            try:
                part = backend_socket.recv(4096)
                if not part: break
                response_from_backend += part
            except socket.timeout:
                break
        
        if response_from_backend:
            client_socket.sendall(response_from_backend)

    except ConnectionRefusedError:
        logging.error(f"Koneksi ke backend {backend_server_address} ditolak. Server tidak berjalan?")
        error_resp = create_error_response(503, "Service Unavailable")
        client_socket.sendall(error_resp)
    
    except Exception as e:
        logging.error(f"Error saat memproses request: {e}")
        error_resp = create_error_response(500, "Internal Server Error")
        client_socket.sendall(error_resp)

    finally:
        if backend_socket:
            backend_socket.close()
        client_socket.close()

def start_load_balancer():
    host = '0.0.0.0'
    port = 55555 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(10)
        logging.warning("="*50)
        logging.warning("🚀 LOAD BALANCER (ROUND-ROBIN) STARTED 🚀")
        logging.warning(f"⚖️  Mendengarkan di port utama: {port}")
        logging.warning(f"🎯 Meneruskan ke backend: {BACKEND_SERVERS}")
        logging.warning("="*50)
        while True:
            connection, client_address = server_socket.accept()
            logging.info(f"Menerima koneksi dari {client_address}")
            thread = threading.Thread(target=handle_request, args=(connection,))
            thread.start()
    except Exception as e:
        logging.error(f"[LOAD BALANCER] Server utama error: {e}")
    finally:
        logging.warning("🛑 Load Balancer sedang dimatikan...")
        server_socket.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        start_load_balancer()
    except KeyboardInterrupt:
        print("\n🛑 Load Balancer dihentikan oleh pengguna.")

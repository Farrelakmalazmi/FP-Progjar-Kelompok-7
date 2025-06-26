import socket
import threading
import json
import itertools

BACKEND_SERVERS = [
    ('127.0.0.1', 60001),
    ('127.0.0.1', 60002),
    ('127.0.0.1', 60003),
]

server_cycler = itertools.cycle(BACKEND_SERVERS)
last_assigned_server = None
is_waiting_for_partner = False
lock = threading.Lock()  

def handle_client_request(connection, address):
    """
    Fungsi ini sekarang memasangkan client berdua-dua.
    """
    global last_assigned_server, is_waiting_for_partner

    print(f"[LOAD BALANCER] Menerima koneksi dari {address}")
    
    server_to_assign = None
    
    with lock:
        if is_waiting_for_partner:
            server_to_assign = last_assigned_server
            is_waiting_for_partner = False  
            print(f"    [PAIRING] Memasangkan {address} dengan pemain sebelumnya di -> {server_to_assign}")
        else:
            server_to_assign = next(server_cycler)
            last_assigned_server = server_to_assign
            is_waiting_for_partner = True 
            print(f"    [NEW GAME] Mengarahkan client pertama {address} ke -> {server_to_assign}. Menunggu pasangan.")

    try:
        response = {"host": server_to_assign[0], "port": server_to_assign[1]}
        connection.sendall(json.dumps(response).encode('utf-8'))
    except Exception as e:
        print(f"[LOAD BALANCER] Error saat mengirim data ke {address}: {e}")
    finally:
        connection.close()

def start_load_balancer():
    host = '0.0.0.0'
    port = 55555

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(10)
        
        print("="*50)
        print("🚀 LOAD BALANCER (PAIRING LOGIC) STARTED 🚀")
        print(f"⚖️  Mendengarkan di port utama: {port}")
        print("="*50)

        while True:
            connection, client_address = server_socket.accept()
            thread = threading.Thread(target=handle_client_request, args=(connection, client_address))
            thread.start()
            
    except Exception as e:
        print(f"[LOAD BALANCER] Server utama error: {e}")
    finally:
        print("🛑 Load Balancer sedang dimatikan...")
        server_socket.close()

if __name__ == "__main__":
    try:
        start_load_balancer()
    except KeyboardInterrupt:
        print("\n🛑 Load Balancer dihentikan oleh pengguna.")


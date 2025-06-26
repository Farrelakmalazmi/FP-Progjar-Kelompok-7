import socket
import logging
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from game_server import SnakeAndLadderServer

game_server = SnakeAndLadderServer()

def ProcessTheClient(connection, address):
    """
    Fungsi ini dijalankan oleh ThreadPool untuk setiap client yang terhubung.
    """
    client_id = f"{address[0]}:{address[1]}"
    print(f"Client baru terhubung: {client_id}")
    
    try:
        connection.settimeout(20.0) 
        name_data = connection.recv(1024).decode('utf-8').strip()
        if not name_data:
            raise Exception("Client tidak mengirim nama.")
        
        connection.settimeout(None)

        game_server.add_client(client_id, connection, name_data)
        
        received_data = ""
        while True:
            data = connection.recv(1024)
            if not data:
                print(f"Client {client_id} terputus.")
                break

            received_data += data.decode('utf-8')
            
            while '\n' in received_data:
                message, received_data = received_data.split('\n', 1)
                if message:
                    try:
                        command = json.loads(message)
                        game_server.handle_command(client_id, command)
                    except json.JSONDecodeError:
                        logging.warning(f"Menerima JSON tidak valid dari {client_id}: {message}")

    except socket.timeout:
        logging.error(f"Koneksi timeout saat menunggu nama dari {client_id}")
    except Exception as e:
        logging.error(f"Error pada koneksi dengan {client_id}: {e}")
    finally:
        print(f"Membersihkan koneksi untuk {client_id}")
        game_server.remove_client(client_id)
        connection.close()

def Server():
    """
    Fungsi utama untuk menjalankan server, socket, dan ThreadPool.
    """
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        my_socket.bind(('0.0.0.0', 55555))
        my_socket.listen(10)
        
        print("="*50)
        print("🐍 SNAKE AND LADDER SERVER STARTED 🐍")
        print("="*50)
        print(f"📡 Server mendengarkan di port 55555")
        print("="*50)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            while True:
                try:
                    connection, client_address = my_socket.accept()
                    executor.submit(ProcessTheClient, connection, client_address)
                except Exception as e:
                    logging.error(f"Error saat menerima koneksi: {e}")
                    
    except Exception as e:
        logging.error(f"Server utama error: {e}")
    finally:
        print("🛑 Server sedang dimatikan...")
        my_socket.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        Server()
    except KeyboardInterrupt:
        print("\n🛑 Server dihentikan oleh pengguna.")
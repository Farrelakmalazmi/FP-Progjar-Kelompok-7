import sys
import os.path
import uuid
import random
import json
import redis
import logging
from datetime import datetime
from glob import glob
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GameState:
    def __init__(self):
        self.players = {}
        self.player_positions = {'1': 0, '2': 0}
        self.current_turn = 1
        self.last_dice_roll = 0
        self.game_active = False
        self.winner = None
        self.last_move_id = None
        self.last_move_path = None
        self.last_moved_player = None
        self.move_start_pos = None

class Board:
    def __init__(self):
        self.snakes_map = {s: e for s, e in [(99, 41), (95, 77), (89, 53), (66, 45), (54, 31), (43, 18), (40, 3), (27, 5)]}
        self.ladders_map = {s: e for s, e in [(4, 25), (13, 46), (33, 49), (42, 63), (50, 69), (62, 81), (74, 92)]}

class GameLogicHandler:
    def __init__(self):
        self.board = Board()

    def roll_dice(self, current_state):
        player_num_int = current_state['current_turn']
        player_num_str = str(player_num_int)
        dice_result = random.randint(1, 6)
        current_state['last_dice_roll'] = dice_result
        current_pos = current_state['player_positions'][player_num_str]
        current_state['move_start_pos'] = current_pos
        path = []
        if current_pos + dice_result > 100:
            path.append({'pos': current_pos, 'type': 'stay'}) 
        else:
            intermediate_pos = current_pos + dice_result
            path.append({'pos': intermediate_pos, 'type': 'normal_land'})
            final_pos = intermediate_pos
            if intermediate_pos in self.board.ladders_map:
                final_pos = self.board.ladders_map[intermediate_pos]
                path.append({'pos': final_pos, 'type': 'ladder_end'})
            elif intermediate_pos in self.board.snakes_map:
                final_pos = self.board.snakes_map[intermediate_pos]
                path.append({'pos': final_pos, 'type': 'snake_end'})
            current_state['player_positions'][player_num_str] = final_pos
        current_state['last_move_id'] = f"move_{uuid.uuid4().hex[:8]}"
        current_state['last_move_path'] = path
        current_state['last_moved_player'] = player_num_int
        if current_state['player_positions'][player_num_str] == 100:
            winner_name = current_state['players'].get(player_num_str, f"Player {player_num_str}")
            current_state['winner'] = winner_name
            current_state['game_active'] = False
        if dice_result != 6 and not current_state['winner']:
            current_state['current_turn'] = 2 if current_state['current_turn'] == 1 else 1
        return current_state

class HttpServer:
    def __init__(self):
        self.types = {'.pdf': 'application/pdf', '.jpg': 'image/jpeg', '.txt': 'text/plain', '.html': 'text/html'}
        self.game_logic = GameLogicHandler()
        try:
            redis_host = "game-progjar.redis.cache.windows.net"
            redis_password = "MASUKKAN_PRIMARY_KEY_DARI_AZURE_DISINI"
            logging.info(f"Menghubungkan ke Redis di host: {redis_host}")
            self.redis_client = redis.Redis(host=redis_host, port=6380, password=redis_password, ssl=True, decode_responses=True)
            self.redis_client.ping()
            logging.info("BERHASIL terhubung ke Azure Cache for Redis!")
        except Exception as e:
            logging.error(f"GAGAL terhubung ke Redis: {e}")
            self.redis_client = None

    def save_game_state(self, game_id, state_dict):
        if not self.redis_client: return False
        try:
            self.redis_client.set(game_id, json.dumps(state_dict))
            return True
        except Exception as e:
            logging.error(f"Error saat menyimpan state: {e}")
            return False

    def get_game_state(self, game_id):
        if not self.redis_client: return None
        try:
            json_string = self.redis_client.get(game_id)
            return json.loads(json_string) if json_string else None
        except Exception as e:
            logging.error(f"Error saat mengambil state: {e}")
            return None

    def response(self, kode=404, message='Not Found', messagebody=b'', headers={}):
        if isinstance(messagebody, str):
            messagebody = messagebody.encode()
        resp_headers = [
            f"HTTP/1.0 {kode} {message}\r\n",
            f"Date: {datetime.now().strftime('%c')}\r\n",
            "Connection: close\r\n",
            "Server: myserver/1.0\r\n",
            f"Content-Length: {len(messagebody)}\r\n"
        ]
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        for kk, vv in headers.items():
            resp_headers.append(f"{kk}: {vv}\r\n")
        resp_headers.append("\r\n")
        return "".join(resp_headers).encode() + messagebody

    def proses(self, data):
        requests = data.split("\r\n")
        baris = requests[0]
        try:
            method, object_address, _ = baris.split(" ", 2)
            logging.info(f"Menerima request: {method} {object_address}")
            if method == 'GET':
                return self.http_get(object_address)
            return self.response(405, 'Method Not Allowed', json.dumps({'error': 'Method not allowed'}))
        except ValueError:
            return self.response(400, 'Bad Request', json.dumps({'error': 'Malformed request line'}))

    def http_get(self, object_address):
        try:
            parsed_url = urlparse(object_address)
            if parsed_url.path == "/game":
                return self.handle_game_request(parse_qs(parsed_url.query))
            return self.response(200, 'OK', json.dumps({'message': 'Web server aktif'}))
        except Exception as e:
            logging.error(f"Error di http_get: {e}", exc_info=True)
            return self.response(500, 'Internal Server Error', json.dumps({'error': str(e)}))

    def handle_game_request(self, params):
        command = params.get('command', [None])[0]
        
        if command == 'FIND_OR_CREATE_GAME':
            player_name = params.get('name', ['Pemain Anonim'])[0]
            for key in self.redis_client.scan_iter("game_*"):
                state = self.get_game_state(key)
                if state and not state.get('game_active') and len(state.get('players', {})) == 1:
                    state['players']['2'] = player_name
                    self.save_game_state(key, state)
                    return self.response(200, 'OK', json.dumps({'game_id': key, 'player_num': 2}))
            
            new_game_id = f"game_{uuid.uuid4().hex[:6]}"
            new_state_obj = GameState()
            new_state_obj.players['1'] = player_name
            self.save_game_state(new_game_id, new_state_obj.__dict__)
            return self.response(200, 'OK', json.dumps({'game_id': new_game_id, 'player_num': 1}))

        game_id = params.get('game_id', [None])[0]
        if not game_id:
            return self.response(400, 'Bad Request', json.dumps({'error': 'game_id dibutuhkan'}))
        
        current_state = self.get_game_state(game_id)
        if not current_state:
            return self.response(404, 'Not Found', json.dumps({'error': f'Game {game_id} tidak ditemukan'}))

        if command == 'START_GAME':
            if len(current_state['players']) < 2:
                return self.response(400, 'Bad Request', json.dumps({'error': 'Butuh 2 pemain'}))
            
            players = current_state['players']
            new_state_obj = GameState()
            new_state_obj.players = players
            new_state_obj.game_active = True
            self.save_game_state(game_id, new_state_obj.__dict__)
            
            return self.response(200, 'OK', json.dumps({'message': 'Game dimulai ulang!'}))

        if command == 'ROLL_DICE':
            player_num = int(params.get('player_num', [0])[0])
            if not current_state.get('game_active') or current_state.get('current_turn') != player_num:
                return self.response(403, 'Forbidden', json.dumps({'error': 'Bukan giliran Anda'}))
            
            new_state = self.game_logic.roll_dice(current_state)
            self.save_game_state(game_id, new_state)
            return self.response(200, 'OK', json.dumps({'status': 'OK', 'message': 'Dice rolled'}))
            
        if command == 'GET_STATE':
            return self.response(200, 'OK', json.dumps(current_state))

        return self.response(400, 'Bad Request', json.dumps({'error': f'Perintah tidak dikenal: {command}'}))

if __name__ == "__main__":
    httpserver = HttpServer()
    logging.info("HttpServer instance created.")
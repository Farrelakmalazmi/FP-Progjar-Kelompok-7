import threading
import time
import json
import logging
import random
from game_state import GameState

class Board:
    def __init__(self):
        self.snakes_map = {s: e for s, e in [(99, 41), (95, 77), (89, 53), (66, 45), (54, 31), (43, 18), (40, 3), (27, 5)]}
        self.ladders_map = {s: e for s, e in [(4, 25), (13, 46), (33, 49), (42, 63), (50, 69), (62, 81), (74, 92)]}

class SnakeAndLadderServer:
    def __init__(self):
        self.clients = {}
        self.game_state = GameState()
        self.board = Board()
        self.lock = threading.Lock()
        
    def add_client(self, client_id, socket, name):
        with self.lock:
            player_numbers_in_use = {c['player_num'] for c in self.clients.values()}
            if len(player_numbers_in_use) >= 2:
                try: socket.sendall((json.dumps({'command':'SERVER_FULL'}) + '\n').encode()); socket.close()
                except: pass
                return
            player_num = 1 if 1 not in player_numbers_in_use else 2
            self.clients[client_id] = {'socket': socket, 'player_num': player_num, 'name': name} 
            print(f"Client {client_id} (Nama: {name}) bergabung sebagai Player {player_num}")
            self.send_to_client(client_id, {'command': 'PLAYER_ASSIGNED', 'player_num': player_num})
            self.broadcast_game_state()
    
    def remove_client(self, client_id):
        with self.lock:
            if client_id in self.clients:
                self.clients.pop(client_id, None)
                print(f"Client {client_id} keluar.")
                self.game_state.reset_game()
                self.broadcast_game_state()
    
    def handle_command(self, client_id, command):
        cmd_type = command.get('command')
        player_num = self.clients.get(client_id, {}).get('player_num')
        
        if cmd_type == 'START_GAME':
            self.start_new_game()
        elif cmd_type == 'ROLL_DICE':
            if player_num == self.game_state.current_turn and self.game_state.game_active:
                self.handle_roll_dice(player_num)

    def handle_roll_dice(self, player_num):
        with self.lock:
            if self.game_state.winner: return

            dice_result = random.randint(1, 6)
            self.game_state.last_dice_roll = dice_result
            
            self.broadcast_message({'command': 'DICE_RESULT', 'dice': dice_result})
            time.sleep(1.5) 

            current_pos = self.game_state.player_positions[player_num]
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
                
                self.game_state.player_positions[player_num] = final_pos
            
            self.broadcast_message({'command': 'PLAYER_MOVE', 'player': player_num, 'path': path})
            time.sleep(0.1) 

            if self.game_state.player_positions[player_num] == 100:
                winner_name = "Unknown"
                for c_id, c_info in self.clients.items():
                    if c_info['player_num'] == player_num:
                        winner_name = c_info['name']
                        break
                self.end_game(winner_name)
                self.broadcast_game_state()
                return

            if dice_result != 6:
                self.game_state.current_turn = 2 if self.game_state.current_turn == 1 else 1
            
            self.broadcast_game_state()
    
    def start_new_game(self):
        with self.lock:
            if len(self.clients) < 2:
                self.broadcast_message({'command': 'GAME_ERROR', 'message': 'Butuh 2 pemain.'})
                return
            print("Game Ular Tangga baru dimulai atau di-reset!")
            self.game_state.reset_game()
            self.game_state.game_active = True
            self.broadcast_game_state()
    
    def end_game(self, winner):
        if not self.game_state.winner:
            self.game_state.game_active = False
            self.game_state.winner = winner
            print(f"Game berakhir! Pemenang: {winner}")
    
    def send_to_client(self, client_id, message):
        try:
            if client_id in self.clients: self.clients[client_id]['socket'].sendall((json.dumps(message) + '\n').encode())
        except: self.remove_client(client_id)
    
    def broadcast_message(self, message):
        for client_id in list(self.clients.keys()): 
            self.send_to_client(client_id, message)

    def broadcast_game_state(self):
        p1_name, p2_name = "Player 1", "Player 2"
        for cid, info in self.clients.items():
            if info['player_num'] == 1: p1_name = info['name']
            if info['player_num'] == 2: p2_name = info['name']
        
        state_msg = { 
            'command': 'GAME_UPDATE', 
            'p1_pos': self.game_state.player_positions.get(1, 0), 
            'p2_pos': self.game_state.player_positions.get(2, 0), 
            'p1_name': p1_name, 
            'p2_name': p2_name, 
            'turn': self.game_state.current_turn, 
            'dice': self.game_state.last_dice_roll, 
            'game_active': self.game_state.game_active, 
            'winner': self.game_state.winner 
        }
        self.broadcast_message(state_msg)

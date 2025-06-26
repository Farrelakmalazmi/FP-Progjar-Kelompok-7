import pygame
import sys
import socket
import json
import threading
import time
import math
import random

def get_game_server_from_balancer(balancer_address):
    """
    Menghubungi Load Balancer untuk mendapatkan alamat server game.
    """
    try:
        print(f"Menghubungi Load Balancer di {balancer_address}...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(balancer_address)
        
        response_data = s.recv(1024).decode('utf-8')
        server_info = json.loads(response_data)
        
        host = server_info['host']
        port = server_info['port']
        
        print(f"Diarahkan ke server game di: {host}:{port}")
        s.close()
        return (host, port)
    except Exception as e:
        print(f"Error saat menghubungi Load Balancer: {e}")
        return None

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake and Ladder Online")
clock = pygame.time.Clock()
back_color = (96, 107, 114)
pla1clr = (0, 211, 255)
pla2clr = (255, 121, 191)

try:
    board_img = pygame.image.load('assets/board.png').convert_alpha() 
    board_img = pygame.transform.scale(board_img, (600, 600))
    dice_images = {i: pygame.transform.scale(pygame.image.load(f'assets/dice{i}.png').convert_alpha(), (150, 150)) for i in range(1, 7)}
except Exception as e:
    print(f"Error memuat aset gambar: {e}"); pygame.quit(); sys.exit()

try:
    dice_roll_sound = pygame.mixer.Sound('sounds/dice_roll.wav')
    pawn_move_sound = pygame.mixer.Sound('sounds/pawn_move.wav')
    snake_slide_sound = pygame.mixer.Sound('sounds/snake_slide.wav')
    win_jingle_sound = pygame.mixer.Sound('sounds/win_jingle.wav')
    ladder_climb_sound = None 
except Exception as e:
    print(f"Peringatan: Tidak semua file suara berhasil dimuat. {e}")
    dice_roll_sound = pawn_move_sound = snake_slide_sound = win_jingle_sound = None

class Board:
    def __init__(self):
        self.pos_map = {} 
        count = 1; box_size = 600 // 10
        for i in range(10):
            for j in range(10):
                if (i % 2) == 0: x, y = j * box_size, (9 - i) * box_size
                else: x, y = (9 - j) * box_size, (9 - i) * box_size
                self.pos_map[count] = (x, y); count += 1

class VisualPlayer:
    def __init__(self, image_path, board_map):
        self.board_map = board_map
        try: self.original_image = pygame.image.load(image_path).convert_alpha(); self.image = pygame.transform.scale(self.original_image, (40, 50))
        except: self.image = pygame.Surface((36, 36)); self.image.fill((255,0,0))
        self.pos = 0; self.x, self.y = -100.0, -100.0
        self.target_x, self.target_y = -100.0, -100.0
        self.is_moving = False; self.speed = 4.0
        self.anim_queue = [] 
        self.pause_until = 0 

    def start_move_animation(self, start_pos, path):
        if self.is_moving or not path: return
        
        self.pos = start_pos
        if self.pos > 0: self.x, self.y = self.board_map[self.pos]; self.target_x, self.target_y = self.x, self.y
        else: self.x, self.y = -100.0, -100.0; self.target_x, self.target_y = self.x, self.y
        
        self.anim_queue = path.copy()
        if self.anim_queue:
            self.is_moving = True
            if pawn_move_sound: pawn_move_sound.play()


    def update_animation(self):
        if not self.is_moving: return
        
        if pygame.time.get_ticks() < self.pause_until:
            return

        if self.x == self.target_x and self.y == self.target_y:
            if self.anim_queue:
                next_stage = self.anim_queue.pop(0)
                self.pos = next_stage['pos']
                self.target_x, self.target_y = self.board_map[self.pos]
                
                if next_stage['type'] == 'normal_land':
                    self.pause_until = pygame.time.get_ticks() + 700 
                
                if next_stage['type'] == 'snake_end':
                    if snake_slide_sound: snake_slide_sound.play()
                    self.speed = 8.0 
                elif next_stage['type'] == 'ladder_end':
                    self.speed = 8.0 
                else:
                    self.speed = 4.0 
            else:
                self.is_moving = False
        
        dx, dy = self.target_x - self.x, self.target_y - self.y
        dist = (dx**2 + dy**2)**0.5
        if dist < self.speed: self.x, self.y = self.target_x, self.target_y
        else: self.x += (dx / dist) * self.speed; self.y += (dy / dist) * self.speed

    def draw(self, is_active_turn):
        if self.pos == 0 and not self.is_moving: return
        
        if self.pos > 0 and self.x == -100.0:
            self.x, self.y = self.board_map[self.pos]
            self.target_x, self.target_y = self.x, self.y

        image_to_draw = self.image; w, h = self.image.get_size()
        if is_active_turn and not self.is_moving:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            new_w = int(w * (1 + pulse * 0.15)); new_h = int(h * (1 + pulse * 0.15))
            image_to_draw = pygame.transform.scale(self.original_image, (new_w, new_h))
        
        pawn_width, pawn_height = image_to_draw.get_size()
        draw_x = self.x + ((600 // 10) - pawn_width) // 2
        draw_y = self.y + ((600 // 10) - pawn_height) // 2
        screen.blit(image_to_draw, (draw_x, draw_y))


def draw_dice(number):
    if number > 0: screen.blit(dice_images[number], (620, 70))

def draw_text(text, font, color, center_pos, align="center"):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        text_surf = font.render(line, True, color)
        text_rect = text_surf.get_rect()
        pos_x = center_pos[0]
        pos_y = center_pos[1] + (i * font.get_linesize()) 

        if align == "center":
            text_rect.center = (pos_x, pos_y)
        else: 
            text_rect.midleft = (pos_x, pos_y)

        screen.blit(text_surf, text_rect)

class GameClient:
    def __init__(self, game_server_address):
        self.server_address = game_server_address
        self.socket, self.connected = None, False
        self.my_player_num, self.game_data = 0, {}
        self.board = Board()
        self.p1_visual = VisualPlayer('assets/pawn_blue.png', self.board.pos_map)
        self.p2_visual = VisualPlayer('assets/pawn_pink.png', self.board.pos_map)
        self.is_dice_animating = False
        self.game_state = "NAME_ENTRY"
        self.player_name = ""
        self.error_message = ""
        self.caption_set = False

    def start_connection_thread(self):
        thread = threading.Thread(target=self._connect_and_listen_worker); thread.daemon = True; thread.start()
    
    def _connect_and_listen_worker(self):
        try: 
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(self.server_address)
            self.connected = True
            self.socket.sendall((self.player_name + '\n').encode('utf-8'))
            self.game_state = "PLAYING"
            self.listen_server()
        except Exception as e: 
            self.error_message = f"Gagal terhubung: {e}"
            self.game_state = "NAME_ENTRY"
            self.connected = False

    def listen_server(self):
        buffer = ""
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data: break
                buffer += data
                while '\n' in buffer: 
                    line, buffer = buffer.split('\n', 1)
                    if line: self.handle_message(json.loads(line))
            except: 
                break
        self.connected = False
        self.error_message = "Koneksi terputus."
        self.game_state = "NAME_ENTRY"

    def handle_message(self, msg):
        command = msg.get('command')
        if command == 'PLAYER_ASSIGNED': 
            self.my_player_num = msg.get('player_num')
        elif command == 'GAME_UPDATE':
            if msg.get('winner') and not self.game_data.get('winner'):
                if win_jingle_sound: win_jingle_sound.play()
            self.game_data = msg
        elif command == 'DICE_RESULT':
            if dice_roll_sound: dice_roll_sound.play()
            threading.Thread(target=self.dice_animation, args=(msg.get('dice', 1),)).start()
        elif command == 'PLAYER_MOVE':
            player_num = msg.get('player')
            path = msg.get('path')
            player_to_move = self.p1_visual if player_num == 1 else self.p2_visual
            start_pos = self.game_data.get(f'p{player_num}_pos', 0)
            player_to_move.start_move_animation(start_pos, path)
        elif command == 'SERVER_FULL': 
            self.error_message = "Server Penuh!"
            self.connected = False
            self.game_state="NAME_ENTRY"

    def dice_animation(self, final_dice):
        self.is_dice_animating = True
        for i in range(15): 
            self.game_data['dice'] = random.randint(1, 6)
            time.sleep(0.06)
        self.game_data['dice'] = final_dice
        self.is_dice_animating = False
    
    def send_command(self, command):
        if self.connected: 
            self.socket.sendall((json.dumps(command) + '\n').encode())

    def run(self):
        font_40 = pygame.font.SysFont("comicsansms", 40)
        font_20 = pygame.font.SysFont("comicsansms", 20)
        font_18 = pygame.font.SysFont("comicsansms", 18, bold=True)
        running = True
        
        while running:
            is_my_turn_now = self.game_data.get('turn') == self.my_player_num
            is_any_pawn_moving = self.p1_visual.is_moving or self.p2_visual.is_moving

            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    running = False
                if self.game_state == "NAME_ENTRY":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN and self.player_name: 
                            self.game_state = "CONNECTING"
                            self.start_connection_thread()
                        elif event.key == pygame.K_BACKSPACE: 
                            self.player_name = self.player_name[:-1]
                        else: 
                            self.player_name += event.unicode
                elif self.game_state == "PLAYING":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if not self.game_data.get('game_active'): 
                                self.send_command({'command': 'START_GAME'})
                            elif is_my_turn_now and not self.is_dice_animating and not is_any_pawn_moving: 
                                self.send_command({'command': 'ROLL_DICE'})
            
            screen.fill(back_color)
            if self.game_state == "NAME_ENTRY":
                draw_text("Masukkan Nama Anda:", font_40, (255,255,255), (WIDTH/2, HEIGHT/2 - 50))
                input_rect = pygame.Rect(WIDTH/2 - 150, HEIGHT/2, 300, 50)
                pygame.draw.rect(screen, (255,255,255), input_rect, 2)
                draw_text(self.player_name, font_40, (255,255,255), (input_rect.x + 10, input_rect.centery), align="left")
                draw_text("Tekan ENTER untuk lanjut", font_20, (200,200,200), (WIDTH/2, HEIGHT/2 + 70))
                if self.error_message: 
                    draw_text(self.error_message, font_20, (255,100,100), (WIDTH/2, HEIGHT/2 + 100))
            elif self.game_state == "CONNECTING":
                draw_text("Menghubungkan ke server...", font_40, (255,255,255), (WIDTH/2, HEIGHT/2))
            elif self.game_state == "PLAYING":
                if self.my_player_num != 0 and not self.caption_set: 
                    pygame.display.set_caption(f"S&L Online - P{self.my_player_num} ({self.player_name})")
                    self.caption_set = True
                
                self.p1_visual.update_animation()
                self.p2_visual.update_animation()
                screen.blit(board_img, (0, 0))
                self.p1_visual.draw(is_active_turn=(self.game_data.get('turn') == 1))
                self.p2_visual.draw(is_active_turn=(self.game_data.get('turn') == 2))
                draw_dice(self.game_data.get('dice', 0))
                
                dark_grey=(53,53,53)
                turn = self.game_data.get('turn')
                draw_text("Turn", font_40, dark_grey, (700, 300))
                if turn == 1: 
                    pygame.draw.circle(screen, pla1clr, (700, 400), 50)
                elif turn == 2: 
                    pygame.draw.circle(screen, pla2clr, (700, 400), 50)
                
                status_text = ""
                if not self.game_data.get('game_active'): 
                    status_text = "Tunggu 2 pemain\nlalu start"
                elif is_my_turn_now: 
                    status_text = "GILIRAN ANDA!\n(SPACE)"
                else: 
                    status_text = f"Menunggu Player {turn}..."
                draw_text(status_text, font_18, dark_grey, (700, 500))

                if self.game_data.get('winner'):
                    winner_name = self.game_data.get('winner')
                    p1_name = self.game_data.get('p1_name', 'Player 1')
                    p2_name = self.game_data.get('p2_name', 'Player 2')
                    winner_display_name = p1_name if winner_name == 'Player 1' else p2_name
                    draw_text(f"{winner_display_name} MENANG!", font_40, (0,200,0), (300, 300))
                
                if not self.connected:
                    draw_text(self.error_message, font_40, (255,0,0), (WIDTH/2, HEIGHT/2))
            
            pygame.display.flip()
            clock.tick(60)
        
        if self.connected: 
            self.socket.close()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    balancer_ip = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    balancer_port = 55555
    
    game_server_address = get_game_server_from_balancer((balancer_ip, balancer_port))
    
    if not game_server_address:
        print("Gagal mendapatkan alamat dari Load Balancer. Aplikasi ditutup.")
        sys.exit()
        
    client = GameClient(game_server_address)
    client.run()

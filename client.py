import pygame
import sys
import socket
import json
import threading
import time
import math
import random
from urllib.parse import urlencode

LOAD_BALANCER_ADDRESS = ('127.0.0.1', 55555)

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake and Ladder Online (HTTP Edition)")
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
        self.board_map=board_map
        try: 
            self.original_image=pygame.image.load(image_path).convert_alpha()
            self.image=pygame.transform.scale(self.original_image,(40,50))
        except: 
            self.image=pygame.Surface((36,36));self.image.fill((255,0,0))
        self.pos=0;self.x,self.y=-100.0,-100.0;self.target_x,self.target_y=-100.0,-100.0
        self.is_moving=False; self.speed=5.0; self.anim_queue=[]; self.pause_until=0
        
    def start_move_animation(self,start_pos,path):
        time.sleep(0.1)
        if self.is_moving or not path:return
        self.pos=start_pos
        self.x,self.y=self.board_map.get(self.pos,(-100,-100));self.target_x,self.target_y=self.x,self.y
        self.anim_queue=path.copy()
        if self.anim_queue and pawn_move_sound: pawn_move_sound.play()
        self.is_moving = True if self.anim_queue else False

    def update_animation(self):
        if not self.is_moving or pygame.time.get_ticks()<self.pause_until:return None
        if self.x==self.target_x and self.y==self.target_y:
            if not self.anim_queue:
                self.is_moving=False
                if self.pos == 100:
                    return "WIN_ANIMATION_DONE"
                return None
            next_stage=self.anim_queue.pop(0);self.pos=next_stage['pos']
            self.target_x,self.target_y=self.board_map[self.pos]
            if next_stage['type']=='normal_land':self.pause_until=pygame.time.get_ticks()+700
            speed_multiplier=2.0 if next_stage['type'] in ['snake_end','ladder_end'] else 1.0
            if next_stage['type']=='snake_end' and snake_slide_sound:snake_slide_sound.play()
            self.speed = 5.0 * speed_multiplier
        dx,dy=self.target_x-self.x,self.target_y-self.y;dist=math.hypot(dx,dy)
        if dist<self.speed:self.x,self.y=self.target_x,self.target_y
        else:self.x+=(dx/dist)*self.speed;self.y+=(dy/dist)*self.speed
        return None

    def draw(self, is_active_turn):
        if self.pos==0 and not self.is_moving:return
        if self.pos > 0 and self.x==-100: self.x,self.y=self.board_map[self.pos];self.target_x,self.target_y=self.x,self.y
        image_to_draw=self.image;w,h=self.image.get_size()
        if hasattr(self, 'original_image') and is_active_turn and not self.is_moving:
            pulse=abs(math.sin(pygame.time.get_ticks()*0.005))
            new_w,new_h=int(w*(1+pulse*0.15)),int(h*(1+pulse*0.15));image_to_draw=pygame.transform.scale(self.original_image,(new_w,new_h))
        pawn_width,pawn_height=image_to_draw.get_size()
        draw_x=self.x+((600//10)-pawn_width)//2;draw_y=self.y+((600//10)-pawn_height)//2
        screen.blit(image_to_draw,(draw_x,draw_y))

def draw_dice(number):
    if number>0:screen.blit(dice_images[number],(620,70))

def draw_text(text,font,color,center_pos,align="center"):
    if text is None: return
    for i,line in enumerate(text.splitlines()):
        text_surf=font.render(line,True,color);text_rect=text_surf.get_rect()
        pos_y=center_pos[1]+(i*font.get_linesize())
        if align=="center":text_rect.center=(center_pos[0],pos_y)
        else:text_rect.midleft=(center_pos[0],pos_y)
        screen.blit(text_surf,text_rect)

def draw_winner_screen(winner_name,winner_color):
    pygame.draw.rect(screen,back_color,(95,95,610,410));pygame.draw.rect(screen,(53,53,53),(100,100,600,400));pygame.draw.rect(screen,back_color,(105,105,590,390))
    large_font=pygame.font.SysFont("comicsansms",90);draw_text("GAME OVER",large_font,(53,53,53),(WIDTH/2,HEIGHT/2-100))
    medium_font=pygame.font.SysFont("comicsansms",50);draw_text("WINNER:",medium_font,(53,53,53),(WIDTH/4+100,HEIGHT/2+50))
    pygame.draw.circle(screen,winner_color,(3*WIDTH//4,HEIGHT//2+50),60)
    name_font=pygame.font.SysFont("comicsansms",25,bold=True);draw_text(winner_name,name_font,(255,255,255),(3*WIDTH//4,HEIGHT//2+50))
    small_font=pygame.font.SysFont("comicsansms",20);draw_text("Tekan SPACE untuk memulai permainan baru",small_font,(53,53,53),(WIDTH/2,HEIGHT-70))

class GameClient:
    def __init__(self):
        self.game_id, self.my_player_num, self.player_name = None, None, ""
        self.game_data, self.error_message = {}, ""
        self.game_state_view = "NAME_ENTRY"
        self.board = Board()
        self.p1_visual = VisualPlayer('assets/pawn_blue.png', self.board.pos_map)
        self.p2_visual = VisualPlayer('assets/pawn_pink.png', self.board.pos_map)
        self.last_animated_move_id = None
        self.running = True
        self.game_over_delay_until = 0
        self.win_sound_played = False

    def send_request(self, params):
        try:
            query_string = urlencode(params)
            request = f"GET /game?{query_string} HTTP/1.1\r\nHost: {LOAD_BALANCER_ADDRESS[0]}:{LOAD_BALANCER_ADDRESS[1]}\r\nConnection: close\r\n\r\n"
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(LOAD_BALANCER_ADDRESS)
            s.sendall(request.encode('utf-8'))
            response_data = b""
            while True:
                part = s.recv(4096)
                if not part: break
                response_data += part
            s.close()
            _, _, body = response_data.partition(b'\r\n\r\n')
            return json.loads(body.decode('utf-8')) if body else None
        except Exception as e:
            self.error_message = f"Koneksi error: {e}"
            return {"error": str(e)}

    def find_and_join_game(self):
        self.game_state_view = "LOBBY"
        screen.fill(back_color)
        draw_text("Mencari game...", pygame.font.SysFont("comicsansms", 40), (255,255,255), (WIDTH/2, HEIGHT/2))
        pygame.display.flip()
        
        params = {'command': 'FIND_OR_CREATE_GAME', 'name': self.player_name}
        response = self.send_request(params)

        if response and 'error' not in response:
            self.game_id = response.get('game_id')
            self.my_player_num = response.get('player_num')
            print(f"Berhasil masuk ke game {self.game_id} sebagai Player {self.my_player_num}")
            pygame.display.set_caption(f"Snake & Ladder - P{self.my_player_num} ({self.player_name})")
            threading.Thread(target=self.polling_worker, daemon=True).start()
        else:
            self.error_message = response.get('error', 'Gagal menemukan atau membuat game.') if response else "Tidak ada balasan dari server."
            self.game_state_view = "NAME_ENTRY"
    
    def process_state_update(self, state_update):
        if not state_update or 'error' in state_update: return
        self.game_data = state_update
        
        new_move_id = self.game_data.get('last_move_id')
        if new_move_id and new_move_id != self.last_animated_move_id:
            self.last_animated_move_id = new_move_id
            
            if dice_roll_sound: dice_roll_sound.play()
            threading.Thread(target=self.dice_animation, args=(self.game_data.get('last_dice_roll', 1),)).start()

            move_path = self.game_data.get('last_move_path')
            if move_path and move_path[0].get('type') != 'stay':
                moved_player_num = self.game_data.get('last_moved_player')
                player_to_move = self.p1_visual if moved_player_num == 1 else self.p2_visual
                start_pos = self.game_data.get('move_start_pos', 0)
                player_to_move.start_move_animation(start_pos, move_path)

    def dice_animation(self, final_dice):
        for _ in range(15): self.game_data['last_dice_roll'] = random.randint(1, 6); time.sleep(0.06)
        self.game_data['last_dice_roll'] = final_dice

    def polling_worker(self):
        while self.running:
            if self.game_id:
                state_update = self.send_request({'command': 'GET_STATE', 'game_id': self.game_id})
                self.process_state_update(state_update)
            time.sleep(0.15)
    
    def run(self):
        font_40 = pygame.font.SysFont("comicsansms", 40)
        font_20 = pygame.font.SysFont("comicsansms", 20)
        font_18 = pygame.font.SysFont("comicsansms", 18, bold=True)
        
        while self.running:
            p1_anim_status = self.p1_visual.update_animation()
            p2_anim_status = self.p2_visual.update_animation()

            if "WIN_ANIMATION_DONE" in [p1_anim_status, p2_anim_status]:
                if not self.win_sound_played:
                    if win_jingle_sound: win_jingle_sound.play()
                    self.win_sound_played = True
                if self.game_over_delay_until == 0:
                    self.game_over_delay_until = pygame.time.get_ticks() + 1200
            
            if self.game_over_delay_until > 0 and pygame.time.get_ticks() >= self.game_over_delay_until:
                self.game_state_view = "GAME_OVER"
            
            if self.game_state_view != "GAME_OVER":
                if self.game_data.get('game_active'): self.game_state_view = "PLAYING"
                elif self.game_id: self.game_state_view = "LOBBY"

            is_my_turn_now = self.game_data.get('current_turn') == self.my_player_num
            is_any_pawn_moving = self.p1_visual.is_moving or self.p2_visual.is_moving
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                    self.running = False
                if self.game_state_view == "NAME_ENTRY":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN and self.player_name: self.find_and_join_game()
                        elif event.key == pygame.K_BACKSPACE: self.player_name = self.player_name[:-1]
                        else: self.player_name += event.unicode
                elif self.game_state_view in ["LOBBY", "PLAYING"]:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        if not self.game_data.get('game_active'):
                            self.send_request({'command': 'START_GAME', 'game_id': self.game_id})
                        elif is_my_turn_now and not is_any_pawn_moving:
                            self.send_request({'command': 'ROLL_DICE', 'game_id': self.game_id, 'player_num': self.my_player_num})
                elif self.game_state_view == "GAME_OVER":
                     if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.win_sound_played = False
                        self.game_over_delay_until = 0
                        self.last_animated_move_id = None
                        self.game_state_view = "LOBBY"
                        self.send_request({'command': 'START_GAME', 'game_id': self.game_id})

            screen.fill(back_color)
            if self.game_state_view == "GAME_OVER":
                winner = self.game_data.get('winner')
                p1_name_from_data = self.game_data.get('players', {}).get('1')
                winner_color = pla1clr if p1_name_from_data == winner else pla2clr
                draw_winner_screen(winner, winner_color)
            elif self.game_state_view == "NAME_ENTRY":
                draw_text("Masukkan Nama Anda:", font_40, (255,255,255), (WIDTH/2, HEIGHT/2 - 50))
                pygame.draw.rect(screen, (255,255,255), (WIDTH/2 - 150, HEIGHT/2, 300, 50), 2)
                draw_text(self.player_name, font_40, (255,255,255), (WIDTH/2 - 140, HEIGHT/2 + 25), align="left")
                draw_text("Tekan ENTER untuk lanjut", font_20, (200,200,200), (WIDTH/2, HEIGHT/2 + 70))
                if self.error_message: draw_text(self.error_message, font_20, (255,100,100), (WIDTH/2, HEIGHT/2 + 100))
            else:
                screen.blit(board_img, (0, 0))
                self.p1_visual.draw(is_active_turn=(self.game_data.get('current_turn') == 1))
                self.p2_visual.draw(is_active_turn=(self.game_data.get('current_turn') == 2))
                draw_dice(self.game_data.get('last_dice_roll', 0))
                turn = self.game_data.get('current_turn')
                draw_text("Turn", font_40, (53,53,53), (700, 300))
                if turn == 1: pygame.draw.circle(screen, pla1clr, (700, 400), 50)
                elif turn == 2: pygame.draw.circle(screen, pla2clr, (700, 400), 50)
                status_text = ""
                if self.game_state_view == "LOBBY": status_text = f"Tunggu pemain...\nGame ID: {self.game_id}\n(SPACE untuk start)"
                elif is_my_turn_now: status_text = "GILIRAN ANDA!\n     (SPACE)"
                else: status_text = f"Menunggu Giliran..."
                draw_text(status_text, font_18, (53,53,53), (700, 520))
            
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    client = GameClient()
    client.run()

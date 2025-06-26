import pygame
import random

display_width = 800
display_height = 600
board_size = 600

back = (96, 107, 114)
pla1clr = (0, 211, 255)
pla2clr = (255, 121, 191)

pygame.init()
pygame.mixer.init()

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Snake And Ladder - Exact Win Rule!')
clock = pygame.time.Clock()

try:
    board_img = pygame.image.load('assets/board.png').convert_alpha() 
    board_img = pygame.transform.scale(board_img, (board_size, board_size))
    dice_images = {i: pygame.transform.scale(pygame.image.load(f'assets/dice{i}.png').convert_alpha(), (150, 150)) for i in range(1, 7)}
    dice_roll_sound = pygame.mixer.Sound('sounds/dice_roll.wav')
    pawn_move_sound = pygame.mixer.Sound('sounds/pawn_move.wav')
    win_jingle_sound = pygame.mixer.Sound('sounds/win_jingle.wav')
    try: snake_slide_sound = pygame.mixer.Sound('sounds/snake_slide.wav')
    except: snake_slide_sound = None
    try: ladder_climb_sound = pygame.mixer.Sound('sounds/ladder_climb.wav')
    except: ladder_climb_sound = None
except pygame.error as e:
    print(f"Error memuat aset: {e}"); pygame.quit(); quit()

crashed = False; roll = False; DONE1 = False
dice_result = 0; show_result_until = 0
is_animating = False 
is_extra_turn = False

def text_objects(text, font, clr):
    return font.render(text, True, clr), font.render(text, True, clr).get_rect()

def WINNER():
    if win_jingle_sound: win_jingle_sound.play()
    winner_color = pla1.clr if turn == 2 else pla2.clr
    pygame.draw.rect(gameDisplay, (back), (95, 95, 610, 410)); pygame.draw.rect(gameDisplay, (53,53,53), (100, 100, 600, 400)); pygame.draw.rect(gameDisplay, (back), (105, 105, 590, 390))
    largeText = pygame.font.SysFont("comicsansms", 90); textSurf, textRect = text_objects("GAME OVER", largeText, (53,53,53)); textRect.center = ((display_width // 2), (display_height // 2 - 100)); gameDisplay.blit(textSurf, textRect)
    mediumText = pygame.font.SysFont("comicsansms", 50); textSurf, textRect = text_objects("WINNER:", mediumText, (53,53,53)); textRect.center = ((display_width // 4 + 100), (display_height // 2 + 50)); gameDisplay.blit(textSurf, textRect)
    pygame.draw.circle(gameDisplay, winner_color, ((3 * display_width // 4), (display_height // 2 + 50)), 60)
    smallText = pygame.font.SysFont("comicsansms", 20); textSurf, textRect = text_objects("Hit Space to Play Again", smallText, (53,53,53)); textRect.center = ((700), (580)); gameDisplay.blit(textSurf, textRect)
    temp = True
    while temp:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: global crashed; crashed = True; temp = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: game_reset(); temp = False
        pygame.display.update()

class board:
    def __init__(self):
        self.pos_map = {} 
        count = 1; box_size = board_size // 10
        for i in range(10):
            for j in range(10):
                if (i % 2) == 0: x, y = j * box_size, (9 - i) * box_size
                else: x, y = (9 - j) * box_size, (9 - i) * box_size
                self.pos_map[count] = (x, y); count += 1
        snakes_pos = [(99, 41), (95, 77), (89, 53), (66, 45), (54, 31), (43, 18), (40, 3), (27, 5)]; ladders_pos = [(4, 25), (13, 46), (33, 49), (42, 63), (50, 69), (62, 81), (74, 92)]
        self.snakes_map = {s: e for s, e in snakes_pos}; self.ladders_map = {s: e for s, e in ladders_pos}
    def draw(self): pass

class player:
    def __init__(self, B, clr, image_path):
        self.board_map, self.snakes, self.ladders = B.pos_map, B.snakes_map, B.ladders_map; self.clr = clr
        try: self.original_image = pygame.image.load(image_path).convert_alpha(); self.image = pygame.transform.scale(self.original_image, (40, 50))
        except pygame.error: self.image = pygame.Surface((36, 36), pygame.SRCALPHA); pygame.draw.circle(self.image, self.clr, (18, 18), 18)
        self.val = 0; self.xpos, self.ypos = -100.0, -100.0 
        self.is_moving = False; self.move_queue = []; self.target_x, self.target_y = self.xpos, self.ypos
        self.speed = 5; self.slide_speed = 8

    def start_move(self, steps):
        if not self.is_moving:
            distance_to_win = 100 - self.val
            
            if self.val > 94: 
                if steps != distance_to_win:
                    print(f"Dadu tidak pas! Anda di posisi {self.val}, butuh dadu angka {distance_to_win} untuk menang.")
                    if pawn_move_sound: pawn_move_sound.play() 
                    pygame.time.wait(200)
                    return False

            if self.val + steps > 100:
                print(f"Dadu terlalu besar! Anda di {self.val}, tidak bisa bergerak {steps} langkah.")
                return False

            for i in range(1, steps + 1):
                self.move_queue.append(self.val + i)
            
            if self.move_queue:
                self.is_moving = True
                self.speed = 5
                if pawn_move_sound: pawn_move_sound.play()
                return True
        return False
        
    def update_animation(self):
        if not self.is_moving: return
        dx, dy = self.target_x - self.xpos, self.target_y - self.ypos; dist = (dx**2 + dy**2)**0.5
        if dist < self.speed: self.xpos, self.ypos = self.target_x, self.target_y
        else: self.xpos += (dx / dist) * self.speed; self.ypos += (dy / dist) * self.speed
        if self.xpos == self.target_x and self.ypos == self.target_y:
            if self.move_queue: self.val = self.move_queue.pop(0); self.target_x, self.target_y = self.board_map[self.val]
            else: self.is_moving = False; self.check_snake_or_ladder()
            
    def check_snake_or_ladder(self):
        if self.val in self.ladders:
            if ladder_climb_sound: ladder_climb_sound.play()
            self.val = self.ladders[self.val]; self.target_x, self.target_y = self.board_map[self.val]
            self.is_moving = True; self.speed = self.slide_speed
        elif self.val in self.snakes:
            if snake_slide_sound: snake_slide_sound.play()
            self.val = self.snakes[self.val]; self.target_x, self.target_y = self.board_map[self.val]
            self.is_moving = True; self.speed = self.slide_speed
        if self.val == 100: global DONE1; DONE1 = True
        
    def draw(self):
        if self.val > 0 or self.is_moving:
            box_size = board_size // 10; pawn_width, pawn_height = self.image.get_size()
            draw_x = self.xpos + (box_size - pawn_width) // 2; draw_y = self.ypos + (box_size - pawn_height) // 2
            gameDisplay.blit(self.image, (draw_x, draw_y))

def draw_dice(number): gameDisplay.blit(dice_images[number], (620, 70))
def game_reset():
    global b, pla1, pla2, turn, DONE1, show_result_until, is_animating, is_extra_turn
    b = board(); pla1 = player(b, pla1clr, 'assets/pawn_blue.png'); pla2 = player(b, pla2clr, 'assets/pawn_pink.png')
    turn = 1; DONE1 = False; show_result_until = 0; is_animating = False
    is_extra_turn = False

game_reset()

while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: crashed = True
        if event.type == pygame.KEYDOWN and not DONE1:
            if event.key == pygame.K_SPACE and not is_animating and show_result_until == 0: roll = True

    if not DONE1:
        gameDisplay.fill(back)
        gameDisplay.blit(board_img, (0, 0))
        dark_grey=(53,53,53);font_40=pygame.font.SysFont("comicsansms",40);font_20=pygame.font.SysFont("comicsansms",20);textSurf,textRect=text_objects("Turn",font_40,dark_grey);textRect.center=((700),(300));gameDisplay.blit(textSurf,textRect);textSurf,textRect=text_objects("Hit Space to Play",font_20,dark_grey);textRect.center=((700),(500));gameDisplay.blit(textSurf,textRect)
        if turn==1:pygame.draw.circle(gameDisplay,pla1.clr,(700,400),50)
        else:pygame.draw.circle(gameDisplay,pla2.clr,(700,400),50)

        if roll:
            if dice_roll_sound: dice_roll_sound.play()
            dice_result = random.randint(1, 6)
            for i in range(15): draw_dice(random.randint(1,6)); pygame.display.update(pygame.Rect(605,50,190,190)); pygame.time.wait(50)
            draw_dice(dice_result)
            show_result_until = pygame.time.get_ticks() + 1000
            roll = False
        
        if show_result_until > 0:
            draw_dice(dice_result)
            if pygame.time.get_ticks() >= show_result_until:
                current_player = pla1 if turn == 1 else pla2
                if current_player.start_move(dice_result): is_animating = True
                else:
                    turn = 2 if turn == 1 else 1
                    is_extra_turn = False
                show_result_until = 0
        
        if is_animating:
            current_player = pla1 if turn == 1 else pla2
            current_player.update_animation()
            if not current_player.is_moving:
                is_animating = False
                if dice_result == 6 and not is_extra_turn: is_extra_turn = True
                else: turn = 2 if turn == 1 else 1; is_extra_turn = False
        
        pla1.draw(); pla2.draw()
    else:
        WINNER()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()
class GameState:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        self.player_positions = {1: 0, 2: 0}
        self.current_turn = 1
        self.last_dice_roll = 0
        self.is_extra_turn = False
        self.game_active = False
        self.winner = None
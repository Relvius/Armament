from src import libtcodpy as lt
from src.map import Map

"""
Window Settings
"""
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 50
LIMIT_FPS = 30
FONT = '../data/fonts/lucida12x12_gs_tc.png'


"""
Entities
"""


class Being:
    def __init__(self, row, col, symbol, color, facing="N"):
        self.row = row
        self.col = col
        self.facing = facing
        self.symbol = symbol
        self.color = color

    def move(self, direction):
        if direction != self.facing:
            self.facing = direction
            return "moved"
        direction_map = {
            "N": (0, -1),
            "S": (0, 1),
            "W": (-1, 0),
            "E": (1, 0)
        }
        target_col = self.col + direction_map[direction][0]
        target_row = self.row + direction_map[direction][1]
        if not area.blocked[target_row][target_col]:
            self.col = target_col
            self.row = target_row
            return "moved"
        else:
            return "bump"

    def draw(self, con):
        lt.console_set_default_foreground(con, self.color)
        lt.console_put_char(con, self.col, self.row, self.symbol, lt.BKGND_NONE)

        # Just an arrow to make direction more obvious. Remove later.
        if self.facing == "N":
            lt.console_put_char(con, self.col, self.row-1, '^', lt.BKGND_NONE)
        elif self.facing == "S":
            lt.console_put_char(con, self.col, self.row+1, 'v', lt.BKGND_NONE)
        elif self.facing == "W":
            lt.console_put_char(con, self.col-1, self.row, '<', lt.BKGND_NONE)
        elif self.facing == "E":
            lt.console_put_char(con, self.col+1, self.row, '>', lt.BKGND_NONE)


"""
Player Control
"""


class Player:
    def __init__(self):
        self.being = Being(15, 15, '@', lt.white)

    def take_turn(self):
        action = None
        control_map = {
            lt.KEY_ESCAPE: (self.leave_game, None),
            lt.KEY_SPACE: (self.reset, None),
            # Movement Keys
            lt.KEY_UP: (self.move, 'N'),
            lt.KEY_DOWN: (self.move, 'S'),
            lt.KEY_LEFT: (self.move, 'W'),
            lt.KEY_RIGHT: (self.move, 'E'),
        }
        while True:
            key = lt.console_check_for_keypress(lt.KEY_PRESSED)
            handler, param = (None, None)
            if key.vk in control_map.keys():
                handler, param = control_map[key.vk]
            elif key.c in control_map.keys():
                handler, param = control_map[key.c]
            if param:
                action = handler(param)
            elif handler:
                action = handler()
            if action:
                return action

    def move(self, direction):
        self.being.move(direction)
        return "moved"

    def leave_game(self):
        return "exit"

    def reset(self):
        return "reset"

"""
Initialization
"""


def new_game():
    # Initialize console & area
    lt.console_set_custom_font(FONT, lt.FONT_TYPE_GRAYSCALE | lt.FONT_LAYOUT_TCOD)
    lt.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Armament', False)

    while not lt.console_is_window_closed():
        lt.sys_set_fps(LIMIT_FPS)
        area = Map(MAP_WIDTH, MAP_HEIGHT)
        # I'd rather not global things, but I can't figure out a way to make collision detection play nicely without it.
        global area

        # Create player entity
        player = Player()
        area.update_fov(player.being.col, player.being.row, player.being.facing)

        # Enter game
        if main(area, player) == "exit":
            return True


"""
Main Loop
"""


def main(area, player):
    while not lt.console_is_window_closed():
        area.draw()
        player.being.draw(area.con)
        lt.console_blit(area.con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
        lt.console_flush()
        player_action = player.take_turn()
        lt.console_clear(0)
        if player_action == "exit":
            return "exit"
        elif player_action == "moved":
            area.update_fov(player.being.col, player.being.row, player.being.facing)
        elif player_action == "reset":
            return "reset"

new_game()
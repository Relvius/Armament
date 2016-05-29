from src import libtcodpy as lt
from src.map import Map
import textwrap

"""
Window Settings
"""
SCREEN_WIDTH = 90
SCREEN_HEIGHT = 65
MAP_WIDTH = 75
MAP_HEIGHT = 55
PANEL_WIDTH = SCREEN_WIDTH - MAP_WIDTH
LOG_HEIGHT = SCREEN_HEIGHT - MAP_HEIGHT
LOG_WIDTH = SCREEN_WIDTH - PANEL_WIDTH
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

    def move(self, direction, strafing=False):
        if (direction != self.facing) and (not strafing):
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


class Weapon:
    def __init__(self, color=lt.white, held="R"):
        self.color = color
        self.held = held

    def swing(self, being):
        # Flash affected tiles.
        lt.console_set_default_background(area.con, lt.white)
        if being.facing == "N":
            lt.console_rect(area.con, being.col-1, being.row-1, 3, 1, True, lt.BKGND_SET)
        elif being.facing == "S":
            lt.console_rect(area.con, being.col-1, being.row+1, 3, 1, True, lt.BKGND_SET)
        elif being.facing == "W":
            lt.console_rect(area.con, being.col-1, being.row-1, 1, 3, True, lt.BKGND_SET)
        elif being.facing == "E":
            lt.console_rect(area.con, being.col+1, being.row-1, 1, 3, True, lt.BKGND_SET)
        lt.console_blit(area.con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, PANEL_WIDTH, 0)
        lt.console_flush()

        # Update held.
        self.held = "R" if self.held == "L" else "L"

    def draw(self, being, con):
        lt.console_set_default_foreground(con, self.color)
        if self.held == "R":
            if being.facing == "N":
                lt.console_put_char(con, being.col+1, being.row, 196, lt.BKGND_NONE)
            elif being.facing == "S":
                lt.console_put_char(con, being.col-1, being.row, 196, lt.BKGND_NONE)
            elif being.facing == "W":
                lt.console_put_char(con, being.col, being.row-1, 179, lt.BKGND_NONE)
            elif being.facing == "E":
                lt.console_put_char(con, being.col, being.row+1, 179, lt.BKGND_NONE)
        elif self.held == "L":
            if being.facing == "S":
                lt.console_put_char(con, being.col + 1, being.row, 196, lt.BKGND_NONE)
            elif being.facing == "N":
                lt.console_put_char(con, being.col - 1, being.row, 196, lt.BKGND_NONE)
            elif being.facing == "E":
                lt.console_put_char(con, being.col, being.row - 1, 179, lt.BKGND_NONE)
            elif being.facing == "W":
                lt.console_put_char(con, being.col, being.row + 1, 179, lt.BKGND_NONE)


class Entity(object):
    def __init__(self):
        self.being = None
        self.weapon = None

    def draw(self, con):
        self.being.draw(con)
        if self.weapon:
            self.weapon.draw(self.being, con)


"""
Player Control
"""


class Player(Entity):
    def __init__(self):
        super(Player, self).__init__()
        self.being = Being(15, 15, '@', lt.white)
        self.weapon = Weapon()

    def take_turn(self):
        action = None
        control_map = {
            lt.KEY_ESCAPE: (self.leave_game, None),
            lt.KEY_SPACE: (self.reset, None),
            # Movement Keys
            lt.KEY_UP: (self.move, 'N'),
            ord('k'): (self.move, 'N'),
            lt.KEY_DOWN: (self.move, 'S'),
            ord('j'): (self.move, 'S'),
            lt.KEY_LEFT: (self.move, 'W'),
            ord('h'): (self.move, 'W'),
            lt.KEY_RIGHT: (self.move, 'E'),
            ord('l'): (self.move, 'E'),
            ord('a'): (self.strafe, None),

            ord('t'): (self.test_message, None),

            ord('s'): (self.swing, None)
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
        check = self.being.move(direction)
        if check == "bump":
            message("Bump.")
        return check

    def strafe(self):
        message('Strafing...')
        while True:
            key = lt.console_check_for_keypress(lt.KEY_PRESSED)
            direction = None
            control_map = {
                lt.KEY_UP: 'N',
                lt.KEY_DOWN: 'S',
                lt.KEY_LEFT: 'W',
                lt.KEY_RIGHT: 'E',
                ord('k'): 'N',
                ord('j'): 'S',
                ord('h'): 'W',
                ord('l'): 'E',
                lt.KEY_ESCAPE: 'cancel'
            }
            if key.vk in control_map.keys():
                direction = control_map[key.vk]
            elif key.c in control_map.keys():
                direction = control_map[key.c]

            if direction == 'cancel':
                message("Canceled strafing.")
                return "bump"
            elif direction:
                check = self.being.move(direction, strafing=True)
                if check == "bump":
                    message("Bump.")
                else:
                    message("Strafing " + direction)
                return check

    def leave_game(self):
        return "exit"

    def reset(self):
        return "reset"

    def test_message(self):
        message('Test.', lt.red)
        return "moved"

    def swing(self):
        # If key pressed in facing direction, swing while taking a step. If 's' is pressed again, swing without stepping.
        message('Swinging...')
        while True:
            key = lt.console_check_for_keypress(lt.KEY_PRESSED)
            direction = None
            control_map = {
                lt.KEY_UP: 'N',
                lt.KEY_DOWN: 'S',
                lt.KEY_LEFT: 'W',
                lt.KEY_RIGHT: 'E',
                ord('k'): 'N',
                ord('j'): 'S',
                ord('h'): 'W',
                ord('l'): 'E',
                ord('s'): 'stay',
                lt.KEY_ESCAPE: 'cancel'
            }
            if key.vk in control_map.keys():
                direction = control_map[key.vk]
            elif key.c in control_map.keys():
                direction = control_map[key.c]

            if direction == self.being.facing:
                check = self.move(direction)
                if check == "bump":
                    message("Unable to swing.", lt.orange)
                    return "bump"
                else:
                    message("Moved and swung " + direction)
                    self.weapon.swing(self.being)
                    return "moved"
            elif direction == 'stay':
                message("Swung " + self.being.facing)
                self.weapon.swing(self.being)
                return "moved"
            elif direction == 'cancel':
                message("Canceling swing.")
                return "bump"


"""
Rendering
"""


def render(area, entities):
    area.draw()
    for entity in entities:
        entity.draw(area.con)

    lt.console_blit(area.con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, PANEL_WIDTH, 0)

    lt.console_flush()


def message(new_msg, color=lt.white):
    new_msg_lines = textwrap.wrap(str(new_msg), LOG_WIDTH - 4)

    for line in new_msg_lines:
        if len(messages) == LOG_HEIGHT - 4:
            del messages[0]
        messages.append((line, color))

    # Render message log.
    lt.console_clear(log)
    # A simple frame
    lt.console_set_default_foreground(log, lt.lighter_grey)
    lt.console_set_default_background(log, lt.darkest_blue)
    lt.console_rect(log, 0, 0, LOG_WIDTH, LOG_HEIGHT, True, lt.BKGND_SET)
    lt.console_print_frame(log, 0, 1, LOG_WIDTH, LOG_HEIGHT-2, False)
    # The messages
    col = 2
    for (line, color) in messages:
        lt.console_set_default_foreground(log, color)
        lt.console_print_ex(log, 2, col, lt.BKGND_NONE, lt.LEFT, line)
        col += 1

    lt.console_blit(log, 0, 0, LOG_WIDTH, LOG_HEIGHT, 0, PANEL_WIDTH, MAP_HEIGHT)
    lt.console_flush()

"""
Initialization
"""


def new_game():
    # Initialize console & area
    lt.console_set_custom_font(FONT, lt.FONT_TYPE_GRAYSCALE | lt.FONT_LAYOUT_TCOD)
    lt.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Armament', False)

    lt.sys_set_fps(LIMIT_FPS)

    global messages, log
    messages = list()
    log = lt.console_new(LOG_WIDTH, LOG_HEIGHT)
    message(' ')  # Ensures log is rendered.

    global panel
    panel = lt.console_new(PANEL_WIDTH, SCREEN_HEIGHT)
    lt.console_set_default_background(panel, lt.darkest_blue)
    lt.console_rect(panel, 0, 0, PANEL_WIDTH, SCREEN_HEIGHT, True, lt.BKGND_SET)
    lt.console_print_frame(panel, 1, 1, PANEL_WIDTH-2, SCREEN_HEIGHT-2, False)
    lt.console_blit(panel, 0, 0, PANEL_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    while not lt.console_is_window_closed():
        global area
        area = Map(MAP_WIDTH, MAP_HEIGHT)
        # I'd rather not global this, but I can't figure out a way to make collision detection play nicely without it.

        # Create player entity
        player = Player()
        area.update_fov(player.being.col, player.being.row, player.being.facing)

        entities = list()
        entities.append(player)

        # Enter game
        if main(area, entities) == "exit":
            return True


"""
Main Loop
"""


def main(area, entities):
    while not lt.console_is_window_closed():
        render(area, entities)
        player = entities[0]
        player_action = player.take_turn()
        if player_action == "exit":
            return "exit"
        elif player_action == "moved":
            area.update_fov(player.being.col, player.being.row, player.being.facing)
        elif player_action == "reset":
            message('New map generated.')
            return "reset"

new_game()

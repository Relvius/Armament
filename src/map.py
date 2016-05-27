from src import libtcodpy as lt


class Map:
    def __init__(self, cols, rows):
        self.f_color = lt.light_amber
        self.f_color_explored = lt.blue
        self.b_color = lt.darkest_amber
        self.b_color_explored = lt.darker_blue

        self.blocked = [[True for x in xrange(cols)] for y in xrange(rows)]
        self.explored = [[False for x in xrange(cols)] for y in xrange(rows)]

        # Create rooms
        rooms = []

        for room in xrange(10):
            w = lt.random_get_int(0, 8, 25)
            h = lt.random_get_int(0, 8, 25)
            col = lt.random_get_int(0, 0, cols - w - 1)
            row = lt.random_get_int(0, 0, rows - h - 1)
            new_room = Rect_Room(col, row, w, h)
            # Check for intersections.
            failed = False
            for other in rooms:
                if new_room.intersect(other):
                    failed = True
                    break
            # Carve out new room.
            if not failed:
                for col in range(new_room.col1 + 1, new_room.col2):
                    for row in range(new_room.row1 + 1, new_room.row2):
                        self.blocked[row][col] = False
                # Create tunnel to previous room.
                if len(rooms) != 0:
                    (new_col, new_row) = new_room.center()
                    (prev_col, prev_row) = rooms[-1].center()
                    if lt.random_get_int(0, 0, 1) == 1:
                        self.horizontal_tunnel(prev_col, new_col, prev_row)
                        self.vertical_tunnel(prev_row, new_row, new_col)
                    else:
                        self.vertical_tunnel(prev_row, new_row, prev_col)
                        self.horizontal_tunnel(prev_col, new_col, new_row)
                rooms.append(new_room)

        # Create console
        self.con = lt.console_new(cols, rows)

        # Create FOV map and cache (cache being for the currently dumb algorithm).
        self.fov = lt.map_new(cols, rows)
        for col in xrange(cols):
            for row in xrange(rows):
                lt.map_set_properties(self.fov, col, row, not self.blocked[row][col], True)
        self.fov_cache = lt.map_new(cols, rows)
        lt.map_copy(self.fov, self.fov_cache)

    def horizontal_tunnel(self, col1, col2, row):
        for col in range(min(col1, col2), max(col1, col2) + 1):
            self.blocked[row][col] = False
            self.blocked[row+1][col] = False

    def vertical_tunnel(self, row1, row2, col):
        for row in range(min(row1, row2), max(row1, row2) + 1):
            self.blocked[row][col] = False
            self.blocked[row][col+1] = False

    def update_fov(self, player_col, player_row, player_facing):
        # This is a really dumb way to do it but lol. First make fov and its cache equal, then build an opaque wall
        # behind the player and calculate FOV with that.
        # I don't want to build my own fov algorithm yet. ._.
        lt.map_copy(self.fov_cache, self.fov)
        height = lt.map_get_height(self.fov)
        width = lt.map_get_width(self.fov)

        if player_facing == "N":
            for i in xrange(width):
                lt.map_set_properties(self.fov, i, player_row+1, False, True)
        elif player_facing == "S":
            for i in xrange(width):
                lt.map_set_properties(self.fov, i, player_row-1, False, True)
        elif player_facing == "W":
            for i in xrange(height):
                lt.map_set_properties(self.fov, player_col+1, i, False, True)
        elif player_facing == "E":
            for i in xrange(height):
                lt.map_set_properties(self.fov, player_col-1, i, False, True)

        lt.map_compute_fov(self.fov, player_col, player_row, 15, True, 2)

    def draw(self):
        for row in xrange(len(self.explored)):
            for col in xrange(len(self.explored[row])):
                char = '#' if self.blocked[row][col] else ' '
                if lt.map_is_in_fov(self.fov, col, row):
                    self.explored[row][col] = True
                    lt.console_put_char_ex(self.con, col, row, char, self.f_color, self.b_color)
                elif self.explored[row][col]:
                    lt.console_put_char_ex(self.con, col, row, char, self.f_color_explored, self.b_color_explored)


class Rect_Room:
    def __init__(self, col, row, w, h):
        self.col1 = col
        self.row1 = row
        self.col2 = col + w
        self.row2 = row + h

    def center(self):
        center_col = (self.col1 + self.col2) / 2
        center_row = (self.row1 + self.row2) / 2
        return (center_col, center_row)

    def intersect(self, other):
        return (self.col1 <= other.col2 and self.col2 >= other.col1 and
                self.row1 <= other.row1 and self.row2 >= other.row1)
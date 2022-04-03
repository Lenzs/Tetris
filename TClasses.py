import pygame as pg
import pygame.event
import numpy
import random

window_dimensions = (500, 560)
arena_dimensions = (250, 500)
arena_top_left = (30, 30)
square_size = 25
line_width = 2
border_width = 2
horizontal_move_cd = 350
switch_piece = False

colours = {'Red': (255, 0, 0), 'Green': (0, 255, 0), 'Blue': (0, 0, 255),
           'Yellow': (255, 255, 0), 'Magenta': (255, 0, 255), 'Orange': (255, 100, 10),
           'Cyan': (0, 255, 255), 'Gray': (128, 128, 128), 'White': (255, 255, 255)}
board = [[(0, 0, 0) for x in range(10)] for y in range(20)]
board_occupied = {(x, y):False for x in range(10) for y in range(20)}
pieces = {'I':['Cyan',
               [['0', '0', '0', '0'],
                ['1', '1', '1', '1'],
                ['0', '0', '0', '0'],
                ['0', '0', '0', '0']]],
          'O':['Yellow',
               [['1', '1'],
                ['1', '1',]]],
          'T':['Magenta',
               [['0', '1', '0'],
                ['1', '1', '1'],
                ['0', '0', '0']]],
          'S':['Green',
               [['0', '1', '1'],
                ['1', '1', '0'],
                ['0', '0', '0']]],
          'Z':['Red',
               [['1', '1', '0'],
                ['0', '1', '1'],
                ['0', '0', '0']]],
          'J':['Blue',
               [['1', '0', '0'],
                ['1', '1', '1'],
                ['0', '0', '0']]],
          'L':['Orange',
               [['0', '0', '1'],
                ['1', '1', '1'],
                ['0', '0', '0']]]}


class TetrisBlock():
    def __init__(self, x, y, piece_type):
        self.x = x
        self.y = y
        self.type = piece_type
        self.colour = colours[pieces[piece_type][0]]
        self.current_layout = pieces[piece_type][1]
        self.next_layout = []

    def get_locations(self, other = None):
        current_loc = []
        if other is None:
            for x in range(len(self.current_layout)):
                for y in range(len(self.current_layout[0])):
                    if self.current_layout[x][y] == '1':
                        current_loc.append((self.x + x, self.y + y))
        else:
            for x in range(len(other)):
                for y in range(len(other[0])):
                    if self.current_layout[x][y] == '1':
                        current_loc.append((self.x + x, self.y + y))
        return current_loc

    def set_x(self, new_x):
        self.x = new_x

    def set_y(self, new_y):
        self.y = new_y

    def get_highest_y(self):
        highest_y = self.get_locations()[0][1]
        for loc in self.get_locations():
            if loc[1] >= highest_y:
                highest_y = loc[1]
        return highest_y

    def get_is_bottom(self):
        #return True in [board_occupied[(loc[0], loc[1]) + 1] for loc in self.get_locations()]
        occupied_squares = []
        for key in board_occupied:
            if board_occupied[key]:
                occupied_squares.append(key)
        for loc in self.get_locations():
            if (loc[0], loc[1] + 1) in occupied_squares:
                print(str((loc[0], loc[1] + 1)) + ' is occupied')
                return True
        return False


    def rotate(self, direction):
        '''new_lst = self.current_layout.copy()
        n = len(new_lst)
        new_lst.reverse()
        for x in range(n):
            for y in range(n - 1, x - 1, -1):
                new_lst[x][y], new_lst[y][x] = new_lst[y][x], new_lst[x][y]
        new_xy = self.get_locations(new_lst)
        if get_locations_valid(new_xy) and True not in [board_occupied[(loc[0], loc[1])] for loc in new_xy]:
            print('valid locations: ' + str(new_xy))
            self.current_layout = new_lst'''
        new_locs = self.get_locations(numpy.rot90(self.current_layout, direction))
        if get_locations_valid(new_locs):
            self.current_layout = numpy.rot90(self.current_layout, direction)


def get_locations_valid(locations):
    highest_y = locations[0][1]
    for loc in locations:
        if loc[1] > highest_y:
            highest_y = loc[1]
    if int(locations[0][0]) > 0 and int(locations[-1][0]) < 9 and int(highest_y) < 19:
        new_locs = [board_occupied[(loc[0], loc[1])] for loc in locations]
        if True not in new_locs:
            return True
    return False


def set_screen(screen):
    screen.fill((0, 0, 0))

    for x in range(len(board)):
        for y in range(len(board[x])):
            pg.draw.rect(screen, board[x][y], (arena_top_left[0] + y * square_size,
                                               arena_top_left[1] + x * square_size,
                                               square_size, square_size), 0)

    for x in range(20 + 1):
        pg.draw.line(screen, colours['Gray'], (arena_top_left[0], arena_top_left[1] + x * square_size),
                     (arena_top_left[0] + arena_dimensions[0], arena_top_left[1] + x * square_size), line_width)
        for y in range(10 + 1):
            pg.draw.line(screen, colours['Gray'], (arena_top_left[0] + y * square_size, arena_top_left[1]),
                         (arena_top_left[0] + y * square_size, arena_top_left[1] + arena_dimensions[1]), line_width)

    pg.draw.rect(screen, colours['White'],
                 (arena_top_left[0], arena_top_left[1], arena_dimensions[0], arena_dimensions[1]), border_width)

def update_display(screen, piece: TetrisBlock):
    for location in piece.get_locations():
        pg.draw.rect(screen, piece.colour, (board_loc_to_screen_loc(location),
                                            (square_size - line_width, square_size - line_width)))

def update_piece(piece: TetrisBlock, direction):
    current_loc = piece.get_locations()
    highest_y = piece.get_highest_y()
    for loc in current_loc:
        if loc[1] > highest_y:
            highest_y = loc[1]

    if direction == 'left' and current_loc[0][0] > 0:
        potential_new_locs = [board_occupied[(loc[0] - 1, loc[1])] for loc in current_loc]
        if True not in potential_new_locs:
            piece.set_x(piece.x - 1)
    elif direction == 'right' and current_loc[-1][0] < 9:
        potential_new_locs = [board_occupied[(loc[0] + 1, loc[1])] for loc in current_loc]
        if True not in potential_new_locs:
            piece.set_x(piece.x + 1)
    elif direction == 'down' and highest_y < 19:
        potential_new_locs = [board_occupied[(loc[0], loc[1] + 1)] for loc in current_loc]
        if True not in potential_new_locs:
            piece.set_y(piece.y + 1)
    elif direction == 'bottom' and highest_y < 19:
        potential_new_locs = [board_occupied[(loc[0], loc[1] + 1)] for loc in current_loc]
        if True not in potential_new_locs:
            piece.set_y(piece.y + 1)
        if highest_y == 19 or True in potential_new_locs:
            pass
        else:
            update_piece(piece, direction)
    update_board_occupancy()

def check_line_clear():
    clean_line = [(0, 0, 0) for i in range(10)]
    index = 19
    while index > 0:
        line = board[index]
        line_clear = True
        for block in line:
            if block == (0, 0, 0):
                line_clear = False
        if line_clear:
            new_index = index
            while new_index > 1:
                board[new_index] = board[new_index - 1]
                new_index -= 1
            board[0] = clean_line
        index -= 1
        if line_clear:
            for x in range(len(board)):
                for y in range(len(board[0])):
                    if board[x][y] == (0, 0, 0):
                        board_occupied[(x, y)] = False
                    else:
                        board_occupied[(x, y)] = True


def visualize_board():
    for x in range(len(board)):
        temp = ''
        for y in range(len(board[0])):
            if board_occupied[(x, y)] == True:
                temp += 'x '
            else:
                temp += 'o '
        print(temp)
    print('\n \n \n')

def update_board_occupancy():
    global board_occupied
    for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y] == (0, 0, 0):
                board_occupied[(x, y)] = False
            else:
                board_occupied[(x, y)] = True
    visualize_board()

def board_loc_to_screen_loc(location):
    return (location[0] * square_size + arena_top_left[0] + line_width,
            location[1] * square_size + arena_top_left[1] + line_width)

def get_random_piece():
    possible_types = [piece for piece in pieces]
    return TetrisBlock(4, 0, random.choice(possible_types))

def run_game():
    running = True
    screen = pg.display.set_mode(window_dimensions)
    set_screen(screen)
    pg.display.flip()
    current_piece = get_random_piece()
    next_piece = get_random_piece()
    clock = pygame.time.Clock()
    vertical_tick = 0
    horizontal_tick = 0
    left_move = False
    right_move = False

    while running:
        global horizontal_move_cd
        tick_speed = 450000
        key_pressed = pygame.key.get_pressed()
        vertical_tick += clock.get_rawtime()
        horizontal_tick += clock.get_rawtime()
        clock.tick()

        if vertical_tick >= tick_speed:
            vertical_tick = 0
            update_piece(current_piece, 'down')

        if horizontal_tick >= horizontal_move_cd:
            horizontal_tick = 0
            if right_move or left_move:
                if horizontal_move_cd > 75:
                    horizontal_move_cd -= horizontal_move_cd - 75

                if left_move:
                    update_piece(current_piece, 'left')
                elif right_move:
                    update_piece(current_piece, 'right')

        if key_pressed[pygame.K_s]:
            vertical_tick *= 1.1

        if key_pressed[pygame.K_a] and not key_pressed[pygame.K_d]:
            left_move = True
        elif key_pressed[pygame.K_d] and not key_pressed[pygame.K_a]:
            right_move = True
        else:
            left_move = False
            right_move = False
            horizontal_move_cd = 350

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.display.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    update_piece(current_piece, 'left')

                elif event.key == pygame.K_d:
                    update_piece(current_piece, 'right')

                elif event.key == pygame.K_RIGHT:
                    current_piece.rotate(1)

                elif event.key == pygame.K_LEFT:
                    current_piece.rotate(3)

                elif event.key == pygame.K_SPACE:
                    update_piece(current_piece, 'bottom')

        if current_piece.get_highest_y() == 19 or current_piece.get_is_bottom():
            for loc in current_piece.get_locations():
                board[loc[1]][loc[0]] = current_piece.colour
                print('placed at ' + str(loc))
                board_occupied[loc] = True
            current_piece = next_piece
            next_piece = get_random_piece()

        check_line_clear()
        set_screen(screen)
        update_display(screen, current_piece)
        pg.display.update()

run_game()

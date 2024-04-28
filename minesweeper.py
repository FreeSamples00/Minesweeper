# goals

# clean up UI
# make grid size / canvas size / mine percentage into sliders preset to a normal 10x10
# add a record system for total wins / losses
# finish gauntlet


# imports
import random as r
import tkinter as tk
from tkinter import ttk
import math
import time as t


# classes
class Tile:
    def __init__(self, x, y):
        self.__mine = False
        self.__revealed = False
        self.__flagged = False
        self.__position = (x, y)
        self.__adjacent_mines = 0

    def is_mine(self):
        return self.__mine

    def is_flagged(self):
        return self.__flagged

    def is_revealed(self):
        return self.__revealed

    def set_tile_number(self):
        x, y = self.__position
        adjacent_mines = 0
        for tile in neighbors_list(x, y):
            if grid[tile[0]][tile[1]].is_mine():
                adjacent_mines += 1
        self.__adjacent_mines = adjacent_mines

    def tile_number(self):
        return self.__adjacent_mines

    def place_mine(self):
        self.__mine = True

    def toggle_flag(self):
        if self.__flagged:
            self.__flagged = False
        else:
            self.__flagged = True

    def reveal(self):
        self.__revealed = True


# functions
def tile_flagged(cords):
    global tile_size, flags, flag_reserves
    x, y = cords.x, cords.y
    x = math.floor(x / tile_size)
    y = math.floor(y / tile_size)
    if not grid[x][y].is_revealed():
        if flags[x][y] == 0:
            flag_reserves -= 1
            x_cord = tile_size / 2 + (x * tile_size)
            y_cord = tile_size / 2 + (y * tile_size)
            font_size = int(tile_size * 0.7)
            flags[x][y] = canvas.create_text(x_cord, y_cord, text='F', font=(number_font, font_size, 'bold'), fill="#ff0000")
        else:
            flag_reserves += 1
            canvas.delete(flags[x][y])
            flags[x][y] = 0
        grid[x][y].toggle_flag()
        if win_check():
            t.sleep(1)
            menu_lock(False)
            game_window.destroy()
        print(f'Flags remaining: {flag_reserves}')


def tile_clicked(cords='', x='', y=''):
    global tile_size, used_blanks, game_window
    clear_list, empty_tiles = set(), []
    if cords != '':
        x, y = cords.x, cords.y
        x = math.floor(x / tile_size)
        y = math.floor(y / tile_size)

    if grid[x][y].is_mine() and not grid[x][y].is_flagged():
        clear_cover(x, y)
        canvas.update()
        end_game('loss')
    elif not grid[x][y].is_flagged():
        clear_list.add((x, y))

        if grid[x][y].tile_number() == 0:
            empty_tiles.append([x, y])
        while len(empty_tiles) > 0:
            x, y = empty_tiles[0]
            used_blanks.add(tuple(empty_tiles[0]))
            for neighbor in neighbors_list(x, y):
                tempx, tempy = neighbor
                clear_list.add((tempx, tempy))
                if grid[tempx][tempy].tile_number() == 0 and (tempx, tempy) not in used_blanks:
                    empty_tiles.append([tempx, tempy])
            empty_tiles.pop(0)

    for tile in clear_list:
        clear_cover(tile[0], tile[1])
        grid[tile[0]][tile[1]].reveal()
        if grid[tile[0]][tile[1]].is_flagged():
            canvas.delete(flags[tile[0]][tile[1]])
            flags[tile[0]][tile[1]] = 0
            grid[tile[0]][tile[1]].toggle_flag()

    if win_check():
        t.sleep(1)
        end_game('win')


def display_grid():
    global game_window, canvas, cover_squares, flags, grid_size, tile_size, canvas_size
    update_values()

    game_window = tk.Tk()
    game_window.title('Minesweeper')
    canvas = tk.Canvas(game_window, width=canvas_size[0], height=canvas_size[1], bg=tile_color)
    canvas.pack()

    # creates a list of lines on the tkinter canvas, forming a grid
    gridlines = []
    for i in range(grid_size[0]):
        x = i * tile_size
        gridlines.append(canvas.create_line(x, 0, x, canvas_size[1], fill=grid_color, width=gridline_width))
    for j in range(grid_size[1]):
        y = j * tile_size
        gridlines.append(canvas.create_line(0, y, canvas_size[0], y, fill=grid_color, width=gridline_width))

    canvas.config(bg=cover_color)
    canvas.bind('<Button-1>', first_click)


def first_click(cords):
    global canvas, stopwatch_start
    x, y = cords.x, cords.y
    x = math.floor(x / tile_size)
    y = math.floor(y / tile_size)
    stopwatch_start = t.time()
    start_game(x, y)


def start_game(_x, _y):
    menu_lock(True)
    global grid, grid_size, cover_squares, flags, used_blanks, canvas, cover_squares, flags, used_blanks, game_window, \
        mine_count, flag_reserves

    # setting up grid list
    grid, used_blanks = [], set()
    for x in range(grid_size[0]):
        grid.append([])
        for y in range(grid_size[1]):
            grid[x].append(Tile(x, y))

    # placing mines
    flag_reserves = mine_count
    for i in range(mine_count):
        x, y = r.randint(0, grid_size[0] - 1), r.randint(0, grid_size[1] - 1)
        while grid[x][y].is_mine() or [x, y] in neighbors_list(_x, _y) or [x, y] == [_x, _y]:
            x, y = r.randint(0, grid_size[0] - 1), r.randint(0, grid_size[1] - 1)
        grid[x][y].place_mine()

    # placing tile numbers
    for y in range(grid_size[1]):
        for x in range(grid_size[0]):
            grid[x][y].set_tile_number()
            display_number(x, y, grid[x][y].tile_number())

    # placing the cover squares
    cover_squares, flags = [], []
    for x in range(grid_size[0]):
        flags.append([])
        cover_squares.append([])
        for y in range(grid_size[1]):
            flags[x].append(0)
            cover_squares[x].append(canvas.create_rectangle(x * tile_size, y * tile_size, (x + 1) * tile_size, (y + 1) * tile_size, outline=grid_color, width=3, fill=cover_color))
            pass
    canvas.config(bg=tile_color)

    canvas.bind('<Button-1>', tile_clicked)
    canvas.bind('<Button-3>', tile_flagged)
    tile_clicked(x=_x, y=_y)
    game_window.mainloop()


def end_game(result):
    global stopwatch_start, gauntlet_mode, gauntlet_times
    print(result)
    t.sleep(1)
    menu_lock(False)
    game_window.destroy()
    stopwatch_result = t.time() - stopwatch_start
    if gauntlet_mode:
        gauntlet_times.append(stopwatch_result)
        if result == 'win':
            continue_gauntlet()
        else:
            end_gauntlet()
    else:
        print(f'Your Time: {reformat_seconds(stopwatch_result)}')


def reformat_seconds(total_seconds):
    if total_seconds > 60:
        seconds = total_seconds % 60
        minutes = (total_seconds - seconds) / 60
        if minutes > 60:
            new_minutes = minutes % 60
            hours = (minutes - new_minutes) / 60
            return f'{hours:.0f}:{new_minutes:02.0f}:{seconds:05.2f}'
        else:
            return f'0:{minutes:02.0f}:{seconds:05.2f}'

    else:
        return f'0:00:{total_seconds:05.2f}'


def clear_cover(x, y):
    global cover_squares
    canvas.itemconfig(cover_squares[x][y], fill='')


def display_number(tile_x, tile_y, number):
    global grid, canvas_size, grid_size, number_font, canvas, tile_size
    x_cord = tile_size / 2 + (tile_x * tile_size)
    y_cord = tile_size / 2 + (tile_y * tile_size) + 1
    if grid[tile_x][tile_y].is_mine():
        letter = 'M'
        font_color = 'black'
        font_size = round((tile_size) * 0.7)
        canvas.create_text(x_cord, y_cord, text=letter, font=(number_font, font_size, 'bold'), fill=font_color)
    elif number != 0:
        font_colors = ([1, '#0000ff'], [2, '#008200'], [3, '#fe0000'], [4, '#000084'], [5, '#840000'], [6, '#008284'],
                       [7, '#840084'], [8, '#757575'])
        font_size = int((tile_size) * 0.7)
        for color in font_colors:
            if color[0] == number:
                font_color = color[1]
        canvas.create_text(x_cord, y_cord, text=str(number), font=(number_font, font_size, 'bold'), fill=font_color)


def neighbors_list(x, y):
    global grid_size
    pops = []
    neighbors = [[(x - 1), (y - 1)], [x, (y - 1)], [(x + 1), (y - 1)],
                 [(x - 1), y],                      [(x + 1), y],
                 [(x - 1), (y + 1)], [x, (y + 1)], [(x + 1), (y + 1)]]
    for i, neighbor in enumerate(neighbors):
        if (not (0 <= neighbor[0] < grid_size[0])) or (not (0 <= neighbor[1] < grid_size[1])):
            pops.append(neighbor)
    for i in pops:
        neighbors.pop(neighbors.index(i))
    return neighbors


def update_values(z=''):
    global grid_size, canvas_size, tile_size, grid_size_selected, difficulty_selected, mine_count

    # grid size
    new_size = grid_size_selected.get()
    canvas_size = [750, 750]
    if new_size == '8x8':
        grid_size[0], grid_size[1] = 8, 8
    if new_size == '16x16':
        grid_size[0], grid_size[1] = 16, 16
    if new_size == '16x32':
        grid_size[0], grid_size[1] = 32, 16
        canvas_size = [1500, 750]
    tile_size = canvas_size[0] / grid_size[0]

    # mine amount
    new_diff = difficulty_selected.get()
    if new_diff == 'Easy':
        temp_percent = .15
    elif new_diff == 'Hard':
        temp_percent = .25
    else:
        temp_percent = .20
    mine_count = round(grid_size[0] * grid_size[1] * temp_percent)


def menu_lock(state):
    global grid_size_input, difficulty_input, start_button
    widgets = [grid_size_input, difficulty_input, start_button]
    if state:
        for widget in widgets:
            widget.configure(state='disabled')
    else:
        for widget in widgets:
            widget.configure(state='normal')
    menu.update()


def win_check():
    global grid
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            if not (grid[x][y].is_revealed() or grid[x][y].is_mine()):
                return False
    return True


def gauntlet_button_pressed():
    global gauntlet_mode
    if gauntlet_mode:
        end_gauntlet()
    else:
        start_gauntlet()


def start_gauntlet():
    menu_lock(True)
    global gauntlet_mode, gauntlet_level
    gauntlet_level = 0
    gauntlet_mode = True
    continue_gauntlet()


def continue_gauntlet():
    global gauntlet_level, grid_size_selected, difficulty_selected
    if gauntlet_level < 2:
        gauntlet_settings = [['8x8', 'Easy'], ['16x16', 'Medium'], ['16x32', 'Hard']][gauntlet_level]
        grid_size_selected = tk.StringVar(value=gauntlet_settings[0])
        difficulty_selected = tk.StringVar(value=gauntlet_settings[1])
        display_grid()
        gauntlet_level += 1
    else:
        end_gauntlet()


def end_gauntlet():
    menu_lock(False)
    global gauntlet_mode, gauntlet_times
    gauntlet_mode = False
    total_time = 0
    for time in gauntlet_times:
        total_time += time
    print(f"Gauntlet time: {reformat_seconds(total_time)}")


# definitions
playing = False

canvas_size, grid_size = [int(), int()], [int(), int()]
tile_size, mine_count, flag_reserves = int(), int(), int()
stopwatch_start = float()
gridline_width = 3

cover_squares = []

gauntlet_mode = False
gauntlet_times = []
gauntlet_level = int()

number_font = 'Terminal'
grid_color = '#7e7e7e'
tile_color = '#b9b9b9'
cover_color = 'light green'
#cover_color = ''

# tkinter
menu = tk.Tk()
menu.title('Menu')
start_button = tk.Button(menu, text='Start', command=display_grid)
grid_size_selected = tk.StringVar(value='8x8')
difficulty_selected = tk.StringVar(value='Medium')
grid_size_input = tk.OptionMenu(menu, grid_size_selected, '8x8', '16x16', '16x32', command=update_values())
difficulty_input = tk.OptionMenu(menu, difficulty_selected, 'Easy', 'Medium', 'Hard', command=update_values())
gauntlet_button = tk.Button(menu, text='Gauntlet', command=gauntlet_button_pressed)


difficulty_input.pack()
grid_size_input.pack()
start_button.pack()
gauntlet_button.pack()


# calls


# mainloop
menu.mainloop()
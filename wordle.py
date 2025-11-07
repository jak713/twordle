import random
import curses
from curses import wrapper
import time
import json
import os

stats_path = 'stats.json'
keyboard = ['qwertyuiop','asdfghjkl','zxcvbnm']
wordle_path = 'words.txt'

valid_path = 'valid.txt'
with open(valid_path, 'r') as f:
    valid_list = [l.strip() for l in f]

def create_data_model():
    data = {
        '1':0,
        '2':0,
        '3':0,
        '4':0,
        '5':0,
        '6':0,
        'X':0,
    }
    return data

def add_data_to_json(row):
    if os.path.exists(stats_path):
        pass
    else:
        stats = create_data_model()
        with open(stats_path, 'w') as file:
            json.dump(stats,file)
    try:
        with open(stats_path, 'r+') as file:
            stats = json.load(file)
            if row != 'X':
                stats[str(row)] += 1
            else:
                stats[row] += 1
            file.seek(0)
            json.dump(stats, file, indent=4)
            file.truncate()
    except Exception as e:
        return e

def show_json_data(stdscr):
    curses.init_pair(99, curses.COLOR_GREEN, curses.COLOR_BLACK)
    BCKGRND = curses.color_pair(99)

    with open(stats_path, 'r') as file:
        stats = json.load(file)
        heights = [value for value in stats.values()]
    
    # back window
    # params are tile_h, tile_w, start_y, start_x
    bckgrnd = curses.newwin(21, 51, 4, 19)
    bckgrnd.bkgd(' ', BCKGRND)
    
    # add labels for x axis
    max_y, max_x = bckgrnd.getmaxyx()
    for i in range(7):
        x_pos = 4 + i*7
        y_pos = max_y - 2
        label = 'X' if i == 6 else str(i+1)
        # out of bounds produces error:
        if 0 <= y_pos < max_y and 0 <= x_pos <= max_x - len(label):
            try:
                bckgrnd.addstr(y_pos, x_pos, label, BCKGRND)
            except curses.error:
                pass
        
    bckgrnd.border()
    bckgrnd.refresh()
    make_chart(heights)

    stdscr.addstr(25,20,"Press 'q' to exit or any other key to play again!", BCKGRND)
    stdscr.refresh()
    key = stdscr.getch()
    if key == ord('q'):
        return False
    else:
        return True

def make_chart(heights):
    RECT = curses.color_pair(99)
    max_height = 18 # for normalisation
    # params are tile_h, tile_w, start_y, start_x
    for i, height in enumerate(heights):
        norm_height = int((height / max(heights)) * max_height) if max(heights) > 0 else 0
        for h in range(norm_height):
            # at the minute hardcoded, but need improvement
            win = curses.newwin(1, 5, 22 - h, 21 + i*7)
            win.bkgd(' ', RECT)
            win.border()
            win.refresh()
            time.sleep(0.05)

def get_wordle(wordle_path) -> str:
    with open(wordle_path, 'r') as file:
        lines = [l.strip() for l in file]
    return random.choice(lines)

def is_valid(word, valid_list) -> bool:
    return word in valid_list

def is_matching(wordle, guess)-> dict:
    matched = {
        'green': [],
        'yellow': [],
        'dark': [],
    }

    wordle_used = [False] * len(wordle)
    # green
    for idx,letter in enumerate(guess):
        if letter == wordle[idx]:
            matched['green'].append(idx)
            wordle_used[idx] = True
    
    # yellow
    for idx, letter in enumerate(guess):
        if idx in matched['green']:
            continue

        found = False
        for w_idx, w_letter in enumerate(wordle):
            if w_letter == letter and not wordle_used[w_idx]:
                matched['yellow'].append(idx)
                wordle_used[w_idx] = True
                found = True
                break
        if not found:
            matched['dark'].append(idx)
    return matched

def is_correct(wordle, guess) -> bool:
    return guess == wordle

def make_wins(color, row, column, letter):
    win = curses.newwin(3, 5, 5+row*3, 30+column*5)
    win.addstr(1,2, letter.upper(), color)
    win.attrset(color)
    win.border()
    win.refresh()
    time.sleep(0.1)

def make_keyboard(color):
    tile_h, tile_w = 3, 3
    y = 24
    x = 27

    offset = 0
    for row in range(len(keyboard)):
            for num in range(len(keyboard[row])):
                win = curses.newwin(tile_h, tile_w, y+row*2, x+num*3+offset)
                win.addstr(1,1, keyboard[row][num].upper())
                win.attrset(color)
                win.border()
                win.refresh()
            offset += 2

def assign_colors_to_keyboard(guess, colors, GREEN, YELLOW, GREY):
    for idx, letter in enumerate(guess):
        if idx in colors['green']:
            color = GREEN
        elif idx in colors['yellow']:
            color = YELLOW
        else:
            color = GREY

        for row in range(len(keyboard)):
            if letter in keyboard[row]:
                col = keyboard[row].index(letter)
                offset = row * 2
                break

        win = curses.newwin(3, 3, 24+row*2, 27+col*3+offset)
        win.addstr(1,1, letter.upper(), color)
        win.attrset(color)
        win.border()
        win.refresh()

def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, 255, curses.COLOR_BLACK)
    curses.init_pair(4,243,curses.COLOR_BLACK)

    GREEN = curses.color_pair(1)
    YELLOW = curses.color_pair(2)
    GREY = curses.color_pair(3)
    DARK = curses.color_pair(4)

    curses.curs_set(False) 
    stdscr.clear()
    stdscr.addstr(3,25,"Welcome to Twordle (<Terminal> Wordle 2)", GREY | curses.A_UNDERLINE)
    stdscr.refresh()

    wordle = get_wordle(wordle_path)

    for j in range(6):
        for i in range(5):
            win = curses.newwin(3, 5, 5+j*3, 30+i*5)
            win.attrset(GREY)
            win.border()
            win.refresh()

    make_keyboard(GREY)

    row = 0
    is_bad_word = False
    is_short_word = False

    while row < 6:
        
        guess = ""
        column = 0
        
        while True:
            if is_bad_word:
                guess = bad_word
                column = 5
                is_bad_word = False

            if is_short_word:
                guess = short_word
                column = len(short_word)
                is_short_word = False

            letter = stdscr.getkey()

            if letter == '\x1b': # Escape button/sequence to quit the app
                return

            if letter in (curses.KEY_ENTER, 10, 13, '\n'):
                break

            if letter in (curses.KEY_BACKSPACE, 127, '\b', '\x7f'):
                if column > 0:
                    column-=1
                    guess = guess[:-1]
                    make_wins(GREY, row, column, " ")
                continue

            while not letter.isalpha():
                letter = stdscr.getkey()

            if column < 5 and len(guess) < 5:
                guess+=str(letter).lower()
                make_wins(GREY, row, column, letter.upper())
                column+=1

        if is_correct(wordle,guess):
            for idx, letter in enumerate(guess):
                make_wins(GREEN, row, idx, letter)
            # dump to stats if win
            add_data_to_json(row+1)
            break

        if len(guess) == 5:
            stdscr.addstr(0,0," "*60)
            stdscr.addstr(0,0,guess + " is a valid word: " + str(is_valid(guess, valid_list)), GREY | curses.A_UNDERLINE)
            if is_valid(guess,valid_list):
                colors = is_matching(wordle, guess)
                for idx, letter in enumerate(guess):
                    if idx in colors['green']:
                        make_wins(GREEN, row, idx, letter)
                    elif idx in colors['yellow']:
                        make_wins(YELLOW, row, idx, letter)
                    else:
                        make_wins(DARK, row, idx, letter)
                row += 1
                assign_colors_to_keyboard(guess, colors, GREEN, YELLOW, DARK)
            else:
                is_bad_word = True
                bad_word = guess
                continue
        else:
            is_short_word = True
            short_word = guess
            continue

    if row == 6:
        add_data_to_json('X')

    stdscr.addstr(23,32,"The wordle was: " + wordle, GREY | curses.A_BLINK)
    stdscr.addstr(2,12,"Press any key to exit or 'p' to play again and 's' to view stats", GREY)

    stdscr.refresh()
    last_key = stdscr.getch()

    if last_key == ord('p'):
        return wrapper(main)
    elif last_key == ord('s'):
        if show_json_data(stdscr):
            return wrapper(main)
        else:
            return
    else:
        return

wrapper(main)

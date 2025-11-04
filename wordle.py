import random
import curses
from curses import wrapper
import time

wordle_path = 'words.txt'
valid_path = 'valid.txt'
with open(valid_path, 'r') as f:
    valid_list = [l.strip() for l in f]

def get_wordle(wordle_path) -> str:
    with open(wordle_path, 'r') as file:
        lines = [l for l in file]
    return random.choice(lines)

def is_valid(word, valid_list) -> bool:
    return word in valid_list

def is_matching(wordle, guess)-> dict:
    matched = {
        'green': [],
        'yellow': [],
        'grey': [],
    }
    for idx,letter in enumerate(guess):
        if letter == wordle[idx]:
            matched['green'].append(idx)
        elif letter in wordle:
            if guess.count(letter) <= wordle.count(letter):
                    matched['yellow'].append(idx)
        else:
            matched['grey'].append(idx)
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

def main(stdscr):

    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4,243,curses.COLOR_BLACK)

    GREEN = curses.color_pair(1)
    YELLOW = curses.color_pair(2)
    GREY = curses.color_pair(3)
    DARK = curses.color_pair(4)

    curses.curs_set(False) 
    stdscr.clear()
    stdscr.addstr(3,25,"Welcome to Twordle (Terminal Wordle 2)", GREY | curses.A_UNDERLINE)
    stdscr.refresh()

    wordle = get_wordle(wordle_path)

    for j in range(6):
        for i in range(5):
            win = curses.newwin(3, 5, 5+j*3, 30+i*5)
            win.attrset(DARK)
            win.border()
            win.refresh()

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
            if letter in (curses.KEY_ENTER, 10, 13, '\n'):
                break

            if letter in (curses.KEY_BACKSPACE, 127, '\b', '\x7f'):
                if column > 0:
                    column-=1
                    guess = guess[:-1]
                    make_wins(DARK, row, column, " ")
                continue

            while not letter.isalpha():
                letter = stdscr.getkey()

            if column < 5 and len(guess) < 5:
                guess+=str(letter).lower()
                make_wins(DARK, row, column, letter.upper())
                column+=1
            

        if len(guess) == 5:
            stdscr.addstr(0,0," "*60)
            stdscr.addstr(0,0,guess + ": " + str(is_valid(guess, valid_list)), GREY | curses.A_UNDERLINE)
            if is_valid(guess,valid_list):

                if is_correct(wordle,guess):
                    for idx, letter in enumerate(guess):
                        make_wins(GREEN, row, idx, letter)
                    break

                else:
                    colors = is_matching(wordle, guess)
                    for idx, letter in enumerate(guess):
                        if idx in colors['green']:
                            make_wins(GREEN, row, idx, letter)
                        elif idx in colors['yellow']:
                            make_wins(YELLOW, row, idx, letter)
                        else:
                            make_wins(GREY, row, idx, letter)
                    row += 1
            else:
                is_bad_word = True
                bad_word = guess
                continue
        else:
            is_short_word = True
            short_word = guess
            continue

    stdscr.addstr(23,32,"The wordle was: " + wordle, GREY | curses.A_BLINK)
    stdscr.addstr(0,32,"Press any key to exit", GREY)

    stdscr.refresh()
    stdscr.getch()

wrapper(main)
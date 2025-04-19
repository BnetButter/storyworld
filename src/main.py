"""
Usage: python3 main.py
"""

import curses
import random
import time
import logging
import sys
import world


logger = logging.getLogger()
loglevel = None if len(sys.argv) == 1 else sys.argv[1]
if loglevel is not None:
    if loglevel == "DEBUG":
        logger.setLevel(logging.DEBUG)  # Set the logging level
    elif loglevel == "INFO":
        logger.setLevel(logging.INFO)
    elif loglevel == "WARNING":
        logger.setLevel(logging.WARNING)
    elif loglevel == "ERROR":
        logger.setLevel(logging.ERROR)
    
    # Create a file handler to write logs to a file
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.NOTSET)
    logger.addHandler(file_handler)

from decryption_alg import factor

n = 2534669

def draw_modal(stdscr, message):
    h, w = stdscr.getmaxyx()
    modal_height, modal_width = 7, 40
    modal_y = (h - modal_height) // 2
    modal_x = (w - modal_width) // 2

    modal = curses.newwin(modal_height, modal_width, modal_y, modal_x)
    modal.bkgd(' ', curses.color_pair(2))
    modal.box()

    modal.addstr(2, (modal_width - len(message)) // 2, message, curses.color_pair(2))
    modal.addstr(4, (modal_width - 20) // 2, "Press any key to close", curses.color_pair(2))

    modal.refresh()
    modal.getch()

def is_valid_move(pos, world_base_map):
    row, col = pos
    rows, cols = world_base_map.shape
    return (
        0 <= row < rows and
        0 <= col < cols and
        world_base_map[row][col] == 1
    )

def write_to_right_sidebar(right_sidebar, text: list[str]):
    right_sidebar.clear()
    max_y, max_x = right_sidebar.getmaxyx()  # Get dimensions of the sidebar window
    logger.info(f"sizeof right side bar: {max_y}, {max_x}")
    right_sidebar.scrollok(True)  # Enable scrolling

    line_height = max_y - 2  # Account for the box frame
    
    # Add lines one by one with a delay
    for i, line in enumerate(text):
        if i >= line_height:
            right_sidebar.scroll(1)  # Scroll up one line
        time.sleep(0.10)
        right_sidebar.addstr(i % line_height, 0, line[:max_x - 4])  # Wrap text inside the sidebar width
        right_sidebar.refresh()

    right_sidebar.refresh()

world_base_map, start_pos = world.generate_map()


def main(stdscr):
    logger.debug("-- MAIN START -- ")

    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    stdscr.bkgd(' ', curses.color_pair(1))
    stdscr.clear()
    stdscr.refresh()

    h, w = stdscr.getmaxyx()
    left_width = w // 4
    right_width = w - left_width

    # Create sidebars using derwin (with parent-child relationship)
    left_sidebar = stdscr.derwin(h, left_width, 0, 0)
    right_sidebar = stdscr.derwin(h, right_width, 0, left_width)
    left_sidebar.bkgd(' ', curses.color_pair(1))
    right_sidebar.bkgd(' ', curses.color_pair(1))

    text_area = right_sidebar.derwin(h-2, right_width-2, 1, 1)
    
    left_sidebar.box()
    right_sidebar.box()
    left_sidebar.addstr(2, 2, "[ Hack Governor Module ] (ENTER)", curses.color_pair(1))
    left_sidebar.refresh()
    right_sidebar.refresh()

    player_pos = list(start_pos)

    # world_base_map is not here, but it is an 2d numpy array. if 

    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord('m'):
            draw_modal(stdscr, "This is a modal dialog!")
        elif key == ord('\n') or key == 10:
            logging.debug(f"Pressed Enter")
            # Simulate random number printout to right sidebar
            random_data = ''.join([str(random.randint(0, 9)) for _ in range(32)])
            text = ["Cracking RSA"] + [ f"n = {a} q = {b}" for a, b in factor(n)]
            write_to_right_sidebar(text_area, text)
            world.render_world(text_area, world_base_map, player_pos)
    
        elif key == ord("w"):
            new_pos = [player_pos[0] - 1, player_pos[1]]
            if is_valid_move(new_pos, world_base_map):
                player_pos = new_pos
                world.render_world(text_area, world_base_map, player_pos)

        elif key == ord("s"):
            new_pos = [player_pos[0] + 1, player_pos[1]]
            if is_valid_move(new_pos, world_base_map):
                player_pos = new_pos
                world.render_world(text_area, world_base_map, player_pos)

        elif key == ord("a"):
            new_pos = [player_pos[0], player_pos[1] - 1]
            if is_valid_move(new_pos, world_base_map):
                player_pos = new_pos
                world.render_world(text_area, world_base_map, player_pos)

        elif key == ord("d"):
            new_pos = [player_pos[0], player_pos[1] + 1]
            if is_valid_move(new_pos, world_base_map):
                player_pos = new_pos
                world.render_world(text_area, world_base_map, player_pos)

                stdscr.refresh()
                left_sidebar.refresh()
                right_sidebar.refresh()

curses.wrapper(main)

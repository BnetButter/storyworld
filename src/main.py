"""
Usage: python3 main.py
"""

import curses
import random
import time
import logging
import sys
import world
import textwrap
import dungeonmaster
import string
from promptwin import PromptWin
#from prompt_handler import open_text_prompt


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

def open_item_prompt(stdscr, item, right_sidebar_width):
    """
    Opens a text prompt in the center of the screen with a message.
    The prompt window will be approximately the size of the right subwindow.
    Allows the user to input text and exits when the user types 'exit'.
    """
    h, w = stdscr.getmaxyx()
    prompt_height = h - 10  # Slightly smaller than the full height
    prompt_width = right_sidebar_width - 8  # Reduce width slightly to center the box
    prompt_y = 5  # Start a bit below the top
    prompt_x = w - right_sidebar_width + 4  # Adjust alignment to center the box better

    # Create a new window for the prompt
    prompt_win = curses.newwin(prompt_height, prompt_width, prompt_y, prompt_x)
    prompt_win.bkgd(' ', curses.color_pair(2))
    prompt_win.box()

    prompt_win.addstr(5, 5, "LOADING...")
    prompt_win.refresh()
    

    # Display the message

    name = item["item_name"]
    text = gs.get_item_description(item)

    # Get available width for wrapping
    max_width = w - 4  # Leave some padding from the edges

    # Wrap the text
    wrapped_lines = textwrap.wrap(text, width=80)

    # Add the name
    prompt_win.addstr(2, 2, name + " -- Press TAB to quit", curses.color_pair(2))

    # Add wrapped lines starting from line 4
    for i, line in enumerate(wrapped_lines[:prompt_height - 4]):
        prompt_win.addstr(4 + i, 2, line, curses.color_pair(2))

    # Refresh the prompt window
    prompt_win.refresh()

    while True:
        n = stdscr.getch()
        if n == ord('\t'):
            return
        


import textwrap

def _render_conversation(win, log, streaming_text, width):
    win.erase()
    win.box()
    win.addstr(2, 2, "Conversation", curses.color_pair(2))
    win.addstr(win.getmaxyx()[0] - 2, 2, "Press TAB to return...", curses.color_pair(2))

    y = 4
    wrap_width = width - 4
    max_y = win.getmaxyx()[0] - 3

    # Draw past conversation
    for speaker, message in log:
        prefix = f"{speaker}: "
        wrapped_lines = textwrap.wrap(message, wrap_width - len(prefix))
        if not wrapped_lines:
            continue

        # First line with speaker label
        if y < max_y:
            win.addstr(y, 2, f"{prefix}{wrapped_lines[0]}", curses.color_pair(2))
            y += 1

        # Remaining lines indented
        for line in wrapped_lines[1:]:
            if y < max_y:
                win.addstr(y, 2 + len(prefix), line, curses.color_pair(2))
                y += 1

        # Add a blank line after each message
        if y < max_y:
            y += 1

    # Draw in-progress reply if it's streaming
    if streaming_text:
        wrapped_lines = textwrap.wrap(streaming_text, wrap_width)
        if y < max_y:
            win.addstr(y, 2, "NPC (typing):", curses.color_pair(2))
            y += 1
        for line in wrapped_lines:
            if y < max_y:
                win.addstr(y, 4, line, curses.color_pair(2))
                y += 1

    logger.debug(streaming_text)
    win.refresh()

 
    
def open_text_prompt(stdscr, item, right_sidebar_width):
    """
    Converse with NPC
    """
    h, w = stdscr.getmaxyx()
    prompt_height = h - 10
    prompt_width = right_sidebar_width - 8
    prompt_y = 4
    prompt_x = w - right_sidebar_width + 4

    promptwin = PromptWin(stdscr)

    promptwin.set_title(item["name"])

    conversation = gs.converse_with_npc(item)
    response = conversation("")

    while True:
        promptwin.append_wrapped("", newline=True)
        for p in response:
            promptwin.append_wrapped(p)
        value = promptwin.capture_input()
        if value == "":
            break
        promptwin.append_wrapped(value, newline=True)
        response = conversation(value)
        
        

def draw_modal(stdscr, message):
    h, w = stdscr.getmaxyx()
    modal_height, modal_width = h - 10, w - 10
    modal_y = (h - modal_height) // 2
    modal_x = (w - modal_width) // 2

    modal = stdscr.derwin(modal_height, modal_width, modal_y, modal_x)
    modal.bkgd(' ', curses.color_pair(2))  # background color for modal
    modal.box()  # draw border

    # Wrap the message text to fit within the modal width
    wrapped_message = textwrap.wrap(message, width=modal_width - 4)

    # Add each line of wrapped message to the modal
    for i, line in enumerate(wrapped_message):
        modal.addstr(2 + i, (modal_width - len(line)) // 2, line, curses.color_pair(2))

    # Add "Press any key to close" message at the bottom
    modal.addstr(modal_height - 2, (modal_width - 20) // 2, "Press any key to close", curses.color_pair(2))

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
    gs = dungeonmaster.GlobalGameState()

    right_sidebar.clear()
    max_y, max_x = right_sidebar.getmaxyx()  # Get dimensions of the sidebar window
    logger.info(f"sizeof right side bar: {max_y}, {max_x}")
    right_sidebar.scrollok(True)  # Enable scrolling

    line_height = max_y - 2  # Account for the box frame
    
    i = 0

    # Add lines one by one with a delay
    while not gs.state_initialized():
        if i >= line_height:
            right_sidebar.scroll(1)  # Scroll up one line
        time.sleep(1)

        right_sidebar.addstr(i % line_height, 0, f"ChatGPT is Generating A World. Please Wait {60-i}s")  # Wrap text inside the sidebar width
        right_sidebar.refresh()
        i += 1


    right_sidebar.refresh()

def update_scrolling_text(scrolling_win, text_lines):
    """
    Updates the scrolling text in the subwindow.
    """
    #scrolling_win.clear()
    scrolling_win.box()  # Redraw the border after clearing
    max_y, max_x = scrolling_win.getmaxyx()
    line_height = max_y - 2  # Account for the box frame

    # Add lines one by one, starting from the second row (index 1)
    for i, line in enumerate(text_lines):
        if i >= line_height:
            scrolling_win.scroll(1)  # Scroll up one line
        scrolling_win.addstr((i % line_height) + 1, 1, line[:max_x - 2])  # Wrap text inside the subwindow width
        scrolling_win.refresh()

def generate_random_ascii(length):
    """
    Generates a random string of ASCII characters of the specified length.

    Args:
        length (int): The length of the random string to generate.

    Returns:
        str: A random string of ASCII characters.
    """
    ascii_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(ascii_characters) for _ in range(length))


def draw_left_box(left_sidebar):
    left_sidebar.box()
    left_sidebar.addstr(2, 2, "[ Hack Governor Module ] (ENTER)", curses.color_pair(1))
    left_sidebar.refresh()

world_base_map, start_pos = world.generate_map()
gs = dungeonmaster.GlobalGameState(start_pos, world_base_map)


def draw_inventory(win):
    win.box()
    win.addstr(2, 2, "[ Hack Governor Module ] (ENTER)", curses.color_pair(1))
    win.addstr(3, 2, "[ Interact with Item   ] ( p )")
    win.addstr(4, 2, "[ Navigate             ] (wasd)")
    win.addstr(5, 2, "------------------------")

    for i, item in enumerate(gs.pickedup_items):
        key = "item_name" if item["type"] == "item" else "name"
        
        button = ""
        if item["type"] == "journal":
            button = f"({item['id']})"

        name = item[key] + button
        win.addstr(6+i, 2, name)
        
    win.refresh()
    
def main(stdscr):
    logger.debug("-- MAIN START -- ")
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    stdscr.bkgd(' ', curses.color_pair(1))
    
    stdscr.refresh()

    h, w = stdscr.getmaxyx()
    left_width = w // 4
    right_width = w - left_width

    # Create sidebars using derwin (with parent-child relationship)
    left_sidebar = stdscr.derwin(h, left_width, 0, 0)
    right_sidebar = stdscr.derwin(h, right_width, 0, left_width)
    left_sidebar.bkgd(' ', curses.color_pair(1))
    right_sidebar.bkgd(' ', curses.color_pair(1))

    text_area = right_sidebar.derwin(h - 2, right_width - 2, 1, 1)

    # Create a small subwindow at the bottom of the left column
    scrolling_height = h // 6  # Make it 1/6th of the screen height
    scrolling_win = left_sidebar.derwin(scrolling_height, left_width - 2, h - scrolling_height - 1, 1)
    scrolling_win.bkgd(' ', curses.color_pair(1))
    scrolling_win.box()

    left_sidebar.box()
    right_sidebar.box()
    draw_inventory(left_sidebar)
    left_sidebar.refresh()
    right_sidebar.refresh()

    
    at_spot = False

    # Example scrolling text
    #random_text = ["Initializing...", "Connecting to server...", "Decrypting data...", "Idle..."]

    # Main game loop
    while True:

        player_pos = gs.player_pos
        random_text = [generate_random_ascii(36) for _ in range(4)]
        current_text = random_text
        key = stdscr.getch()
        
        if key == ord('\n') or key == 10:
            logging.debug(f"Pressed Enter")
            # Simulate random number printout to right sidebar
            random_data = ''.join([str(random.randint(0, 9)) for _ in range(32)])
            text = ["Cracking RSA"] + [ f"n = {a} q = {b}" for a, b in factor(n)]
            write_to_right_sidebar(text_area, text)
            logger.debug(f"{gs.location_index}")
            scenario = gs.init_state["scenario"]["scenario"]
            right_sidebar.clear()
            draw_modal(right_sidebar, scenario)
            draw_left_box(left_sidebar)
            right_sidebar.box()
            world.render_world(text_area, world_base_map)

        
        # Check if player reaches a specific position
        if key == ord("p"):  # Example position
            item = gs.get_item_near_me(*player_pos)
            if item is not None:
                
                if item["type"] == "item":
                    gs.add_item(item)
                    draw_inventory(left_sidebar)
                    open_item_prompt(stdscr, item, right_width)
                elif item["type"] == "journal":
                    gs.add_item(item)
                    draw_inventory(left_sidebar)
                elif item["type"] == "npc":
                    open_text_prompt(right_sidebar, item, right_width)
                world.render_world(text_area, world_base_map)
                right_sidebar.refresh()
            
        elif player_pos != [5, 5] and at_spot:  # Example position
            at_spot = False
        elif key == ord("w"):
            new_pos = [player_pos[0] - 1, player_pos[1]]
            if is_valid_move(new_pos, world_base_map):
                gs.player_pos = new_pos
                world.render_world(text_area, world_base_map)

        elif key == ord("s"):
            new_pos = [player_pos[0] + 1, player_pos[1]]
            if is_valid_move(new_pos, world_base_map):
                gs.player_pos = new_pos
                world.render_world(text_area, world_base_map)

        elif key == ord("a"):
            new_pos = [player_pos[0], player_pos[1] - 1]
            if is_valid_move(new_pos, world_base_map):
                gs.player_pos = new_pos
                world.render_world(text_area, world_base_map)

        elif key == ord("d"):
            new_pos = [player_pos[0], player_pos[1] + 1]
            if is_valid_move(new_pos, world_base_map):
                gs.player_pos = new_pos
                world.render_world(text_area, world_base_map)

        # Trigger an in-game event to update the scrolling text
        page_trigger = False
        if key == ord('1') and gs.has_journal(1):  # Example event trigger
            journal_num = 0
            page_trigger = True
            #current_text =
            update_scrolling_text(scrolling_win, [f"Opening Journal page: {journal_num}"])
        page_trigger = False
        if key == ord('2') and gs.has_journal(2):  # Example event trigger
            journal_num = 1
            page_trigger = True
            #current_text = 
            update_scrolling_text(scrolling_win, [f"Opening Journal page: {journal_num}"])
        page_trigger = False
        if key == ord('3') and gs.has_journal(3):  # Example event trigger
            journal_num = 2
            page_trigger = True
            #current_text = 
            update_scrolling_text(scrolling_win, [f"Opening Journal page: {journal_num}"])
        page_trigger = False
        if key == ord('4') and gs.has_journal(4):  # Example event trigger
            journal_num = 3
            page_trigger = True
            #current_text = 
            update_scrolling_text(scrolling_win, [f"Opening Journal page: {journal_num}"])
        page_trigger = False
        if key == ord('5') and gs.has_journal(5):  # Example event trigger
            journal_num = 4
            page_trigger = True
            #current_text = 
            update_scrolling_text(scrolling_win, [f"Opening Journal page: {journal_num}"])
        page_trigger = False
        if key == ord('6') and gs.has_journal(6):  # Example event trigger
            journal_num = 5
            page_trigger = True
            #current_text = 
            update_scrolling_text(scrolling_win, [f"Opening Journal page: {journal_num}"])
        page_trigger = False
        if key == ord('7') and gs.has_journal(7):  # Example event trigger
            journal_num = 6
            page_trigger = True
            #current_text = 
            update_scrolling_text(scrolling_win, [f"Opening Journal page: {journal_num}"])
        page_trigger = False
        if key == ord('8') and gs.has_journal(8):  # Example event trigger
            journal_num = 7
            page_trigger = True
            #current_text = 
            update_scrolling_text(scrolling_win, [f"Opening Journal page: {journal_num}"])
        page_trigger = False
        if key == ord('9') and gs.has_journal(9):  # Example event trigger
            journal_num = 8
            page_trigger = True
            #current_text = 
            update_scrolling_text(scrolling_win, [f"Opening Journal page: {journal_num}"])
        page_trigger = False
        if key == ord('0') and gs.has_journal(0):  # Example event trigger
            journal_num = 9
            page_trigger = True
            #current_text = 
            update_scrolling_text(scrolling_win, [f"Opening Journal page: {journal_num}"])

        # Restore random scrolling text after event
        elif key == ord('r'):  # Example reset trigger
            current_text = random_text
            update_scrolling_text(scrolling_win, current_text)

        if not page_trigger:
            # Update scrolling text periodically
            update_scrolling_text(scrolling_win, [f"Navigating: x={player_pos[0]} y={player_pos[1]}"])#current_text)
        page_trigger = False

        stdscr.refresh()
        left_sidebar.refresh()
        right_sidebar.refresh()

curses.wrapper(main)

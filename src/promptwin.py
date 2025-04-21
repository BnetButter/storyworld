import curses
import curses.textpad
import textwrap

class PromptWin:

    def __init__(self, parent: 'curses._CursesWindow', height_offset=3, width_offset=5):
        parent_y, parent_x = parent.getmaxyx()

        # Calculate dynamic size and position with offsets
        height = parent_y - height_offset * 2
        width = parent_x - width_offset * 2
        start_y = height_offset
        start_x = width_offset

        # Create the modal window (mainscr) with dynamic size
        self.mainscr = parent.derwin(height, width, start_y, start_x)
        self.mainscr.clear()
        

        # Draw the border
        self.mainscr.box()

        self.title_area = self.mainscr.derwin(1, width - 2, 1, 1)
        self.text_area = self.mainscr.derwin(height - 6, width - 2, 2, 1)

        
        self.input_area = self.mainscr.derwin(3, width - 2, height - 5, 1)
        self.input_area.addstr(0, 0, "INPUT")

        self.mainscr.addstr(height - 2, 1, "Press TAB to Exit")
        self.mainscr.refresh()
    
    def clear(self):
        # Clear all areas
        self.mainscr.clear()
        self.title_area.clear()
        self.text_area.clear()
        self.input_area.clear()


        # Refresh to update the screen
        self.mainscr.refresh()
        self.title_area.refresh()
        self.text_area.refresh()
        self.input_area.refresh()

    
    def refresh(self):
        self.mainscr.refresh()
    
    def set_title(self, text):
        _, max_x = self.title_area.getmaxyx()
        self.title_area.addstr(0, 0, text[:max_x])
        self.title_area.refresh()
    

    def capture_input(self) -> str:
        curses.curs_set(1)  # Show blinking cursor
        self.input_area.clear()
        self.input_area.refresh()

        # Create a Textbox wrapper around the input_area
        textbox = curses.textpad.Textbox(self.input_area, insert_mode=True)
            
        _tab_pressed = False  # Track if user exits with Tab

        def validator(ch):
            if ch == 10:  # Enter
                return 7  # Submit input
            elif ch == 9:  # Tab
                self._tab_pressed = True
                return 7  # Exit textbox without submitting
            return ch

        user_input = textbox.edit(validator).strip()

        curses.curs_set(0)  # Hide cursor

        # Optional: return empty string or None if Tab was used to escape
        return "" if _tab_pressed else user_input

    def append_wrapped(self, text: str, newline=False):
        self.text_area.scrollok(True)
        self.text_area.idlok(True)  # Optional for better performance

        max_y, max_x = self.text_area.getmaxyx()
        wrapped_lines = textwrap.wrap(text, width=max_x)
        if newline:
            self.text_area.addstr("\n")
        for line in wrapped_lines:
            self.text_area.addstr(line)
        self.text_area.refresh()

def main(stdscr):
    # Initialize the screen
    curses.curs_set(0)  # Hide the cursor for a cleaner UI
    stdscr.clear()  # Clear the screen

    def open_modal():
        # Create the PromptWin modal
        prompt_win = PromptWin(stdscr)

        prompt_win.set_title("NPC Dialogue here")

        while True:
            value = prompt_win.capture_input()
            if value == "":
                prompt_win.clear()
                break
            for i in range(30):
                prompt_win.append_wrapped(value)

    while True:
        ch = stdscr.getch()
        if ch == ord("p"):
            open_modal()
        elif ch == "q":
            break
        

    # Clean up and exit
    curses.endwin()


if __name__ == "__main__":
    curses.wrapper(main)
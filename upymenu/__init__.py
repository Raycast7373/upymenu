import math


class Menu:
    def __init__(self, title, render_title=False):
        self.title = title

        # TODO: implement if we should render a title.. can be done, by adding a noop option to the option list?
        self.render_title = render_title
        self.lcd = None
        self.options = []
        self.parent_menu = None

        # We start on the first option by default (not 0 to prevent ZeroDivision errors )
        self.focus = 1
        self.viewport = None
        self.active = False
        self.oldfocus = 0
    # Chunk the options to only render the ones in the viewport
    def _chunk_options(self):
        for i in range(0, len(self.options), self.lines):
            yield self.options[i : i + self.lines]

    # Get the current chunk based on the focus position
    def _current_chunk(self):
        return math.floor(self.focus / (self.lines + 1))  # current chunk

    # Starts the menu, used at root level to start the interface.
    # Or when navigating to a submenu or parten
    def start(self, lcd):
        self.lcd = lcd  # Assign the LCD to the menu.
        self.columns = lcd.cols  # Get the columns of the LCD
        self.lines = lcd.rows  # And the line
        self.active = True  # Set the screen as active

        # Chunk the list and calculate the viewport:
        self.options_chunked = list(self._chunk_options())
        self.render()
        self._render_cursor()
        return self

    # Renders the menu, also when refreshing (when changing select)
    def render(self):
        # We only render the active screen, not the others
        if not self.active or not self.options_chunked:
            return

        self.viewport = self.options_chunked[self._current_chunk()]
        self.lcd.clear()
        self.lcd.set_cursor(0, 0)

        #self._render_cursor()
        self._render_options()

    def _render_cursor(self):
        # Calculate the starting index based on focus position and number of lines
        start_index = (self.focus - 1) % len(self.options)

        # Render the cursor:
        for l in range(self.lines):
            option_index = (start_index + l) % len(self.options)

            self.lcd.set_cursor(19, l)
            # If the current position matches the focus, render the cursor
            if l == (self.focus - 1) % self.lines:
                self.lcd.print("<")
            else:
                self.lcd.print(" ")

    def _render_options(self):
        # Render the options:
        for l, option in enumerate(self.viewport):
            self.lcd.set_cursor(0, l)  # Move to the line
            # And render the longest possible string on the screen
            self.lcd.print(option.title[: self.columns - 1])

    # Add an option to the menu (could be an action or submenu)
    def add_option(self, option):
        if type(option) not in [Menu, MenuAction, MenuNoop]:
            raise Exception(
                "Cannot add option to menu (required Menu, MenuAction or MenuNoop)"
            )
        self.options.append(option)


   # Function that checks if it needs to load a new menu
    def CheckIfUpdateMenu(self):
        #Old_dec = float(self.oldfocus / self.lines) % 1 # calculate old num decimal and only keep the decimals
        #New_dec = float(self.focus / self.lines) % 1 # calculate new num decimal and only keep the decimals
        #Steps = 1 / self.lines # calculate the steps
        Old_dec = float(self.oldfocus / len(self.viewport)) % 1 # calculate old num decimal and only keep the decimals
        New_dec = float(self.focus / len(self.viewport)) % 1 # calculate new num decimal and only keep the decimals
        Steps = 1 / len(self.viewport) # calculate the steps
        if Old_dec == 0.0 and New_dec == Steps or Old_dec == Steps and New_dec == 0.0:
            return True
        else:
            return False

    # Focus on the next option in the menu
    def focus_next(self):
        self.oldfocus = self.focus
        self.focus += 1
        # Wrap around
        if self.focus > len(self.options):
            self.focus = 1
        if self.CheckIfUpdateMenu():
            self.render()
        self._render_cursor()

    # Focus on the previous option in the menu
    def focus_prev(self):
        self.oldfocus = self.focus
        self.focus -= 1
        if self.focus < 1:
            self.focus = len(self.options)
        if self.CheckIfUpdateMenu():
            self.render()
        self._render_cursor()
            

    # Focus on the option n in the menu
    def focus_set(self, n):
        self.oldfocus = self.focus
        self.focus = n
        if self.CheckIfUpdateMenu():
            self.render()
        self._render_cursor()

    # Choose the item on which the focus is applied
    def choose(self):
        chosen_option = self.options[self.focus - 1]

        if type(chosen_option) == Menu:
            return self._choose_menu(chosen_option)
        elif type(chosen_option) == MenuAction:
            chosen_option.cb()  # Execute the callback function
            return self
        elif type(chosen_option) == MenuNoop:
            return self

    # Navigate to the parent (if the current menu is a submenu)
    def parent(self):
        if self.parent_menu:
            self.active = False
            return self.parent_menu.start(self.lcd)

    def _choose_menu(self, submenu):
        self.active = False
        submenu.parent_menu = self
        return submenu.start(self.lcd)  # Start the submenu or parent


class MenuAction:
    def __init__(self, title, callback, value=None):
        self.title = title
        self.callback = callback
        self.value = value
    def cb(self):
        return self.callback(self.value)


class MenuNoop:
    def __init__(self, title):
        self.title = title

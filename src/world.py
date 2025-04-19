import curses
from typing import List, Tuple
import pathlib
import random

import numpy as np
from noise import snoise2


def render_world(curses_win: curses.window, game_map: List[List[str]], player_pos: Tuple[int, int]) -> None:
    max_rows = len(game_map)
    max_cols = len(game_map[0])
    
    # Get window size
    height, width = curses_win.getmaxyx()

    # Define buffer zone
    v_buf = 4
    h_buf = 10

    # Player's global position
    prow, pcol = player_pos

    # Default top-left of the window in map coords
    view_row = max(0, prow - height // 2)
    view_col = max(0, pcol - width // 2)

    # Adjust the view so the player stays inside the buffer
    if prow - view_row < v_buf:
        view_row = max(0, prow - v_buf)
    elif prow - view_row >= height - v_buf:
        view_row = min(max_rows - height, prow - height + v_buf + 1)

    if pcol - view_col < h_buf:
        view_col = max(0, pcol - h_buf)
    elif pcol - view_col >= width - h_buf:
        view_col = min(max_cols - width, pcol - width + h_buf + 1)

    # Clamp the view in case we're near the map edges
    view_row = max(0, min(view_row, max_rows - height))
    view_col = max(0, min(view_col, max_cols - width))

    # Clear the window before drawing
    curses_win.erase()

    # Draw the portion of the map in the current view
    for y in range(height):
        for x in range(width):
            map_y = view_row + y
            map_x = view_col + x
            if 0 <= map_y < max_rows and 0 <= map_x < max_cols:
                num = game_map[map_y][map_x]
                if num == 0:
                    char = '#'
                else:
                    char = ' '
                curses_win.addch(y, x, char)

    # Draw the player at their relative position
    player_screen_y = prow - view_row
    player_screen_x = pcol - view_col
    curses_win.addch(player_screen_y-1 if player_screen_y - 1 >= 0 else 0, player_screen_x, '@')

    # Refresh the window
    curses_win.refresh()


import pathlib
import random

import numpy as np
from noise import snoise2

# This script generates a 2D grid world of clear spaces and obstacles. The world
# is represented by a 2D array of zeroes and ones. Zeroes are clear free space
# and ones are an obstacle. The grid data is written to a CSV file and a supporting
# configuration data file is generated describing the grid world.
#
# Note: To run this file locally you'll need to install numpy, matplotlib, and noise
# `pip install matplotlib`
# `pip install numpy`
# `pip install noise`


def generate_grid(width, height, scale, threshold, octaves, persistence, lacunarity) -> np.ndarray:

    grid = np.zeros((height, width), dtype=int)

    for y in range(height):
        for x in range(width):
            noise_value = snoise2(x / scale, y / scale, octaves, persistence, lacunarity)
            normalized_value = (noise_value + 1) / 2
            
            if normalized_value > threshold:
                grid[y, x] = 1  # Obstacle
            else:
                grid[y, x] = 0  # Clear space

    return grid

def find_start_coordinate(grid: np.ndarray):
    """
    Find a random clear space to serve as the starting point for a search vehicle.

    Args:
        grid: A 2D grid of zeros and ones.

    Returns:
        A tuple of row and column indecies into the grid where the search vehicle
        should start.
    """
    row_index = None
    col_index = None

    while True:
        random_index = np.random.randint(0, grid.size)

        # Convert the index to 2D coordinates
        row_index = random_index // grid.shape[1]
        col_index = random_index % grid.shape[1]

        # Check if the coordinate is clear of obstacles
        random_cell = grid[row_index, col_index]
        if random_cell == 0:
            break
    
    return row_index, col_index

def generate_map():
    width = 256  # Width of the grid
    height = 128  # Height of the grid
    scale = 50.0
    threshold = 0.4  # Threshold for determining if noise value becomes an obstacle
    octaves = 2
    persistence = random.uniform(0.25, 4.5)
    lacunarity = random.uniform(1, 5)
    grid = generate_grid(width, height, scale, threshold, octaves, persistence, lacunarity)
    
    while True:
        y, x = random.randint(32, 96), random.randint(50, 200)
        if grid[y][x] == 1:
            return grid, (y, x)
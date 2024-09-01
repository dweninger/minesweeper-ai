import cv2 as cv
from time import sleep

import numpy as np
from windowcapture import WindowCapture
from vision import Vision
import pyautogui
import random
import keyboard

# List the name of each window available for capture
#WindowCapture.list_window_names()

# initialize the WindowCapture class
wincap = WindowCapture('Minesweeper Online - Play Free Online Minesweeper - Google Chrome')
vision_unclicked_block = Vision('unclicked_block.png')
vision_one = Vision('one.png')
vision_two = Vision('two.png')
vision_three = Vision('three.png')
vision_four = Vision('four.png')
vision_five = Vision('five.png')
vision_restart2 = Vision('restart2.png')
vision_restart3 = Vision('restart3.png')
vision_flag = Vision('flag.png')
game_over = False
stop_loop = False
paused = False

# the minimum and maximum distance in pixles away 
#   from a tile to be considered "next to" another tile
x_threshold = (15, 42)
y_threshold = (15, 42)

# checking difference between needle and haystack image
THRESHOLD = 0.9
# checking how big to make reference "needle" images
SCALE_FACTORS = [round(0.5 + 0.05 * i, 2) for i in range(50)]

# click the restart button when game over
def restart(restart2_points):
    target = wincap.get_screen_position(restart2_points[0])
    pyautogui.click(x=target[0], y=target[1])
    
# look at board size and scale the needle images accordingly
def calibrate_scale_factor(scale_factors):
    board_screenshot = wincap.get_screenshot()
    best_scale = None
    max_matches = 0
    
    for scale in scale_factors:
        # resize the needle image according to the scale factor
        resized_needle = cv.resize(vision_unclicked_block.needle_image, None, fx=scale, fy=scale)
        
        # perform template match
        result = cv.matchTemplate(board_screenshot, resized_needle, cv.TM_CCOEFF_NORMED)
        locations = np.where(result >= THRESHOLD) # threshold
        num_matches = len(list(zip(*locations[::-1])))
        
        if num_matches > max_matches:
            max_matches = num_matches
            best_scale = scale
            
    scale_coord_thresholds(best_scale)
    
    return best_scale

def scale_coord_thresholds(best_scale):
    global x_threshold, y_threshold
    # Convert the tuple to a list
    x_threshold = list(x_threshold)
    y_threshold = list(y_threshold)

    # Update the values
    x_threshold[0] = x_threshold[0] * best_scale
    x_threshold[1] = x_threshold[1] * best_scale
    y_threshold[0] = y_threshold[0] * best_scale
    y_threshold[1] = y_threshold[1] * best_scale

    # Convert back to a tuple if needed
    x_threshold = tuple(x_threshold)
    y_threshold = tuple(y_threshold)

# find and click a random unclicked tile (when there are no better moves)
def click_rand_tile(unclicked_block_points):
    num_unclicked_blocks = len(unclicked_block_points)
    rand_unclicked_block_index = random.randint(0, num_unclicked_blocks)
    target = wincap.get_screen_position(unclicked_block_points[rand_unclicked_block_index])
    pyautogui.click(x=target[0], y=target[1])

# find the distance between two points. used for finding the eight tiles surrounding another tile    
def euclidean_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def check_number(number, number_points, unclicked_block_points, flag_points):
    # check each number tile to see if the tiles around it are either mines or can be clicked
    for number_point in number_points:
        filtered_unlicked_points = []
        filtered_unclicked_flag_points = [point for point in flag_points if
                                    x_threshold[0] <= euclidean_distance(number_point, point) <= x_threshold[1] and
                                    y_threshold[0] <= euclidean_distance(number_point, point) <= y_threshold[1]]
        
        filtered_unclicked_block_points = [point for point in unclicked_block_points if
                                    x_threshold[0] <= euclidean_distance(number_point, point) <= x_threshold[1] and
                                    y_threshold[0] <= euclidean_distance(number_point, point) <= y_threshold[1]]
        
        filtered_unlicked_points = [point for point in unclicked_block_points + flag_points if
                                    x_threshold[0] <= euclidean_distance(number_point, point) <= x_threshold[1] and
                                    y_threshold[0] <= euclidean_distance(number_point, point) <= y_threshold[1]]

        # if there is only one unclicked point next to the point of interest
        # it is a mine, so right click and mark with a flag
        if len(filtered_unlicked_points) == number:
            for point in filtered_unclicked_block_points:
                target = wincap.get_screen_position(point)
                pyautogui.rightClick(x=target[0], y=target[1])
                return True
                
        # find all flags surrounding the point of interest
        if len(filtered_unclicked_flag_points) >= number: 
            for point in filtered_unclicked_block_points:
                target = wincap.get_screen_position(point)
                pyautogui.click(x=target[0], y=target[1])
                return True
  
    return False

def stop():
    global stop_loop
    stop_loop = True
    
def pause():
    global paused
    paused = True
    
def resume():
    global paused
    paused = False

keyboard.add_hotkey('q', stop)
keyboard.add_hotkey('p', pause)
keyboard.add_hotkey('r', resume)

best_scale = calibrate_scale_factor(SCALE_FACTORS)

while not stop_loop:
    if paused:
        sleep(0.1)
        continue
    
    # get an updated image of the game
    screenshot = wincap.get_screenshot()
    # get each type of tile in separate lists
    unclicked_block_points = vision_unclicked_block.findClickpoints(screenshot, THRESHOLD, best_scale, debug_mode='rectangles')
    one_points = vision_one.findClickpoints(screenshot, THRESHOLD, best_scale, debug_mode='points')
    two_points = vision_two.findClickpoints(screenshot, THRESHOLD, best_scale, debug_mode='points')
    three_points = vision_three.findClickpoints(screenshot, THRESHOLD, best_scale, debug_mode='points')
    four_points = vision_four.findClickpoints(screenshot, THRESHOLD, best_scale, debug_mode='points')
    five_points = vision_five.findClickpoints(screenshot, THRESHOLD, best_scale, debug_mode='points')
    restart2_points = vision_restart2.findClickpoints(screenshot, 0.95, best_scale, debug_mode='points')
    
    flag_points = vision_flag.findClickpoints(screenshot, THRESHOLD, best_scale, debug_mode='points')
    # save each of the number points in a list so as to be able to easily loop through later
    number_points_list = [None, one_points, two_points, three_points, four_points, five_points]
    # restart button appears indicating game over
    game_over = restart2_points and len(restart2_points) > 0
    
    if game_over:
        # restart the game if lost
        restart(restart2_points)
    elif len(unclicked_block_points) > 0:
        for i in range(1, 5):
            found_num = check_number(i, number_points_list[i], unclicked_block_points, flag_points)
            if found_num == True:
                break
        if found_num == False:
            print("Random selection.")
            click_rand_tile(unclicked_block_points)
    else:
        print("Game Won!")
        win_restart = input("Restart? (y/n): ")
        if win_restart.lower() == "y":
            restart3_points = vision_restart3.findClickpoints(screenshot, 0.95, best_scale, debug_mode='points')
            restart(restart3_points)
        else:
            break

    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break
    
    # a little useless right now  
    sleep(0.011)

print('Done.')

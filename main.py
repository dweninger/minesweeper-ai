import cv2 as cv
from time import sleep
from windowcapture import WindowCapture
from vision import Vision
import pyautogui
import random

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
vision_flag = Vision('flag.png')
game_over = False
# the minimum and maximum distance in pixles away from a tile to be considered "next to" another tile
x_threshold = (15, 42)
y_threshold = (15, 42)

# click the restart button when game over
def restart(restart2_points):
    target = wincap.get_screen_position(restart2_points[0])
    pyautogui.click(x=target[0], y=target[1])

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
    # check each number tile to see if the tiles around it are either bombs or can be clicked
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
        # it is a bomb, so right click and mark with a flag
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

while(True):

    # get an updated image of the game
    screenshot = wincap.get_screenshot()
    # get each type of tile in separate lists
    unclicked_block_points = vision_unclicked_block.findClickpoints(screenshot, 0.8, scale_factors=[1.0], debug_mode='rectangles')
    one_points = vision_one.findClickpoints(screenshot, 0.8, scale_factors=[1.0], debug_mode='points')
    two_points = vision_two.findClickpoints(screenshot, 0.8, scale_factors=[1.0], debug_mode='points')
    three_points = vision_three.findClickpoints(screenshot, 0.8, scale_factors=[1.0], debug_mode='points')
    four_points = vision_four.findClickpoints(screenshot, 0.8, scale_factors=[1.0], debug_mode='points')
    five_points = vision_five.findClickpoints(screenshot, 0.8, scale_factors=[1.0], debug_mode='points')
    restart2_points = vision_restart2.findClickpoints(screenshot, 0.95, scale_factors=[1.0], debug_mode='points')
    flag_points = vision_flag.findClickpoints(screenshot, 0.8, scale_factors=[1.0], debug_mode='points')
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
            if found_num:
                break
        if not found_num:
            print("Random selection.")
            click_rand_tile(unclicked_block_points)
    else:
        print("Game Won!")

    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break
      
    sleep(1)

print('Done.')
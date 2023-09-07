import cv2
import numpy as np
import pyautogui

def findClickpoints(haystack_image_path, needle_image_path, threshold=0.8, scale_factors=[1.0], debug_mode='None'):
    # Load the haystack and needle images
    haystack_image = cv2.imread(haystack_image_path)
    needle_image = cv2.imread(needle_image_path)

    # Get the dimensions of the needle image
    needle_height, needle_width = needle_image.shape[:2]
    
    method = cv2.TM_CCOEFF_NORMED

    # Perform template matching at multiple scales
    matches = []

    for scale in scale_factors:
        resized_needle = cv2.resize(needle_image, None, fx=scale, fy=scale)
        result = cv2.matchTemplate(haystack_image, resized_needle, method)
        locations = np.where(result >= threshold)  # Threshold value to filter matches
        location_tuples = list(zip(*locations[::-1])) # Zip to readable location tuples

        for loc in location_tuples:
            rect = [int(loc[0]), int(loc[1]), int(needle_width * scale), int(needle_height * scale)]
            matches.append(rect)
            matches.append(rect)
        if len(matches) > 0:
            break

    # Group matches to find one per needle/haystack pair
    if len(matches) > 0:
        matches = np.array(matches)
        matches, weights = cv2.groupRectangles(matches, groupThreshold=1, eps=0.5)

    line_color = (0, 255, 0)
    line_type = 2
    marker_color = (255, 0, 255)
    marker_type = cv2.MARKER_CROSS
    
    points = []
    
    # Draw rectangles around matched areas
    for (x, y, w, h) in matches:
        
        # find the center of each unclicked box
        center_x = x + int(w/2) 
        center_y = y + int(h/2)
        points.append((center_x, center_y))
        
        # Debug to draw rectangles around matches
        if debug_mode == 'rectangles':
            top_left = (x, y)
            bottom_right = (x+w, y+h)
            cv2.rectangle(haystack_image, top_left, bottom_right, line_color, line_type)
            
        # Debug to draw crosses at click points
        elif debug_mode == 'points':
            cv2.drawMarker(haystack_image, (center_x, center_y), marker_color, marker_type)

    if debug_mode:
        # Save the result image
        output_image = 'result_image.png'
        cv2.imwrite(output_image, haystack_image)
    
    return points

points = findClickpoints('board.png', 'unclicked_block.png', debug_mode='points')
print(points)
points = findClickpoints('board.png', 'unclicked_block.png', debug_mode='rectangles')
print(points)
print('Done.')

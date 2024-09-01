import cv2
import numpy as np

class Vision:
    needle_image = None
    needle_width = 0
    needle_height = 0
    method = None

    def __init__(self, needle_image_path, method=cv2.TM_CCOEFF_NORMED):
        self.needle_image = cv2.imread(needle_image_path)
        # Get the dimensions of the needle image
        self.needle_height, self.needle_width = self.needle_image.shape[:2]
        self.method = method

    def findClickpoints(self, haystack_image, threshold=0.8, scale=1.0, debug_mode='None'):
        # Perform template matching at multiple scales
        matches = []

        resized_needle = cv2.resize(self.needle_image, None, fx=scale, fy=scale)
        result = cv2.matchTemplate(haystack_image, resized_needle, self.method)
        locations = np.where(result >= threshold)  # Threshold value to filter matches
        location_tuples = list(zip(*locations[::-1])) # Zip to readable location tuples

        for loc in location_tuples:
            rect = [int(loc[0]), int(loc[1]), int(self.needle_width * scale), int(self.needle_height * scale)]
            matches.append(rect)
            matches.append(rect)

        # Group matches to find one per needle/haystack pair
        if len(matches) > 0:
            matches = np.array(matches)
            matches, weights = cv2.groupRectangles(matches, groupThreshold=1, eps=0.5)

        line_color = (0, 255, 0)
        line_type = 2
        marker_color = (255, 0, 255)
        marker_type = cv2.MARKER_CROSS
        
        points = []
        
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
            # Show the result image
            #output_image = 'result_image.png'
            #cv2.imwrite(output_image, haystack_image)
            cv2.imshow('Matches', haystack_image)
        
        return points

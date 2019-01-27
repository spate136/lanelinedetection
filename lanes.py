import cv2
import numpy as np
import matplotlib.pyplot as plt

def convert_to_canny(image):
    # Converts RGB pixels to grayscale to simplify computation
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Applies a 5x5 gaussian blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Converts image to detect sharp edges by finding the derivative of two adjacent pixels
    # if the derivative is high enough and within the range (with a 1:3 proportion),
    # this line displays edges as white on a black background
    canny_image = cv2.Canny(blur, 50, 150)
    return canny_image

def region_of_interest(image):
    height = image.shape[0]
    triangle = np.array([(200, height), (1100, height), (550, 250)])
    mask = np.zeros_like(image)
    polygons = [triangle]

    # Fills in the triangle of interest with white on a back mask
    cv2.fillPoly(mask, polygons, 255)

    # Bitwise ANDs the derivative and region of interest to obtain edges of road
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image

def display_lines(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None:
        for x1, y1, x2, y2 in lines:
            cv2.line(line_image, (x1, y1), (x2, y2), (127, 255, 0), 5)
        return line_image

def average_slope_intercept(image, lines):
    left_fit = []
    right_fit = []
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        #print(parameters)
        slope = parameters[0]
        intercept = parameters[1]
        if slope < 0:
            left_fit.append((slope, intercept))
        else:
            right_fit.append((slope, intercept))
        #print(left_fit, "left")
        #print(right_fit, "right")
    left_fit_average = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0)
    #print(left_fit_average, "left")
    #print(right_fit_average, "right")
    left_line = make_coordinates(image, left_fit_average)
    right_line = make_coordinates(image, right_fit_average)
    return np.array([left_line, right_line])

def make_coordinates(image, line_parameters):
    slope, intercept = line_parameters
    #print(image.shape)
    y1 = image.shape[0]
    y2 = int(y1* (3/5))
    # y = mx + b  ->  x = (y - b)/m
    x1 = int((y1 - intercept)/slope)
    x2 = int((y2 - intercept)/slope)
    return np.array([x1, y1, x2, y2])

# image = cv2.imread('test_image.jpg')
# lane_image = np.copy(image) # Copies the image
# canny_image = convert_to_canny(lane_image)
# cropped_image = region_of_interest(canny_image)
# # 54:00
# lines = cv2.HoughLinesP(cropped_image, 2, np.pi/180, 100, np.array([]), minLineLength=40, maxLineGap=5)
# averaged_lines = average_slope_intercept(lane_image, lines)
# line_image = display_lines(lane_image, averaged_lines)
#
# # Makes lines more apparent ad clear
# combined_image = cv2.addWeighted(lane_image, 0.8, line_image, 1, 1)
# cv2.imshow('result', combined_image)
# cv2.waitKey(0)

cap = cv2.VideoCapture("test2.mp4")
while(cap.isOpened()):
    _, frame = cap.read()
    canny_image = convert_to_canny(frame)
    cropped_image = region_of_interest(canny_image)
    # 54:00
    lines = cv2.HoughLinesP(cropped_image, 2, np.pi / 180, 100, np.array([]), minLineLength=40, maxLineGap=5)
    averaged_lines = average_slope_intercept(frame, lines)
    line_image = display_lines(frame, averaged_lines)

    # Makes lines more apparent ad clear
    combined_image = cv2.addWeighted(frame, 0.65, line_image, 1, 1)
    cv2.imshow('result', combined_image)
    # 1:24:00
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
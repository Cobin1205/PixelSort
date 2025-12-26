import PIL as pil
from PIL import Image
import pygame
import sys
import random

def get_pixels_between_points(p1, p2):
    x1, y1 = int(round(p1[0])), int(round(p1[1]))
    x2, y2 = int(round(p2[0])), int(round(p2[1]))

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    steep = dy > dx

    # Swap coordinates if steep
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap points if necessary
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    dx = x2 - x1
    dy = abs(y2 - y1)
    error = dx / 2
    ystep = 1 if y1 < y2 else -1

    y = y1
    pixels = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if steep else (x, y)
        pixels.append(coord)
        error -= dy
        if error < 0:
            y += ystep
            error += dx

    if swapped:
        pixels.reverse()  # ensures pixels are in the same order as user movement

    return pixels

file = "trusselSort.jpg"

pygame.init()

if file[len(file)-4:] == ".jpg":  
    #Set dimensions of pygame window
    with Image.open(file) as img:
        img.save(file.replace("jpg", "png"))
        file = file.replace("jpg", "png")

#Get pygame version of image
image = pygame.image.load(file)
imageRect = image.get_rect()
width, height = image.get_size()
screen = pygame.display.set_mode((width, height))

lines = []
currentLinePoints = set()

drawing = False

start = ()
lastPoint = tuple()

running = True
while running:
    for event in pygame.event.get():
        #X clicked means whole process is shut down
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        #Enter pressed means done selecting areas, process image
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                running = False

            if event.key == pygame.K_z:
                lines = lines[:len(lines)-1]

    #draw the image
    screen.fill((255, 255, 255))
    screen.blit(image, imageRect)

    #put pixel in set when mouse is down
    mouseButtons = pygame.mouse.get_pressed()
    if mouseButtons[0]:
        pixelPos = pygame.mouse.get_pos()
        currentLinePoints.add(pixelPos)
        
        #add points between last point and new
        #to avoid gaps when moving mouse
        if lastPoint == tuple():
            lastPoint = pixelPos
        else:
            for point in get_pixels_between_points(lastPoint, pixelPos):
                currentLinePoints.add(point)
            lastPoint = pixelPos

        #if mouse clicked down, set the start
        if not drawing:
            start = pixelPos
            drawing = True

    #if mouse lifted up, draw straight line from end to beginning
    #and save it to the lines
    if drawing and not mouseButtons[0]:
        for point in get_pixels_between_points(lastPoint, start):
            currentLinePoints.add(point)
        lines.append(tuple(currentLinePoints))
        lastPoint = tuple()
        start = tuple()
        currentLinePoints = set()
        drawing = False

    #draw completed shapes blue
    for line in lines:
        for point in line:
            screen.set_at(point, (0, 0, 255))

    #draw current lines green
    for point in currentLinePoints:
        screen.set_at(point, (0, 255, 0))

    pygame.display.flip()

pygame.quit()


#Begin Processing Image
#--------------------------------------------------------------------------------------------------------

def get_brightness(color_rgb):
    """
    Calculates perceived brightness using the standard luminance formula.
    Weights are based on human perception of different color intensities.
    """
    R, G, B = color_rgb
    # Formula for perceived luminance/brightness
    brightness = (0.299 * R + 0.587 * G + 0.114 * B)
    return brightness

inputNotApproved = True
while inputNotApproved:
    print("Minimum bleed? (integer)")
    minBleed = input()
    print("Maximum bleed? (integer)")
    maxBleed = input()

    try:
        minBleed = int(minBleed)
        maxBleed = int(maxBleed)
        break
    except:
        continue

    if isinstance(minBleed, int) and isinstance(maxBleed, int):
        inputNotApproved = False

#Get a list of all drawn pixels
allPixels = []
for line in lines:
    for point in line:
        allPixels += [point]

try:
    pilImage = Image.open(file)
except FileNotFoundError:
    print("Image not found. Please check the file path.")
    exit()

pixelMap = pilImage.load()
mapWidth, mapHeight = pilImage.size

intervals = []
intervaling = False

#Iterate left to right
for x in range(mapWidth):
    top = tuple()
    intervaling = False
    #iterate top to bottom
    for y in range(mapHeight):
        #if we hit a top pixel, make it the top and keep scanning down
        if not intervaling and (x, y) in allPixels:
            top = (x, y)
            intervaling = True
            continue
        #hit bottom of interval. Add interval to list and reset values
        elif intervaling and (x, y) in allPixels and abs(top[1] - y) > 10:
            bleedAmount = random.randint(minBleed, maxBleed)
            yVal = max(0, min(y + bleedAmount, mapHeight))
            intervals.append((top, (x, yVal)))
            top = tuple()
            intervaling = False

for interval in intervals:
    #Sort color interval vertically
    ogPixelColors = []
    for i in range(interval[0][1], interval[1][1]):
        ogPixelColors.append(pilImage.getpixel((interval[0][0], i)))
    sortedColors = sorted(ogPixelColors, key=get_brightness)

    j = 0
    for i in range(interval[0][1], interval[1][1]):
        pixelMap[interval[0][0], i] = sortedColors[j]
        j += 1 



pilImage.show()
pilImage.save("output.jpg")
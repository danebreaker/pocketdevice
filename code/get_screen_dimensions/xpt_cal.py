from machine import Pin, SPI
from sys import implementation
from os import uname
import ili9341
from xglcd_font import XglcdFont
import mySetupX

print(implementation.name)
print(uname()[3])
print(uname()[4])

print(SPI(0))
print(SPI(1))

minX = maxX = minY = maxY = 500

def xpt_touch(x, y):
    global xptTouch
    global minX, maxX, minY, maxY
    
    touchXY = xptTouch.get_touch()
    rawX = xptTouch.send_command(xptTouch.GET_X)
    rawY = xptTouch.send_command(xptTouch.GET_Y)
    
    if rawX != 0:
        if rawX > maxX:
            maxX = rawX
        elif rawX < minX:
            minX = rawX
    if rawY != 0:    
        if rawY > maxY:
            maxY = rawY
        elif rawY < minY:
            minY = rawY
    
    display.fill_circle(x, y, 2, ili9341.color565(0, 255, 0))
    print(str(x) + ":" + str(y) + " / " + str(rawX) + ":" + str(rawY))
    
    if touchXY != None:
        touchX = touchXY[0]
        touchY = touchXY[1]
        display.fill_circle(touchX, touchY, 2, ili9341.color565(255, 0, 0))
        print(str(touchX) + ":" + str(touchY))
        
    xReading = "X: " + str(minX) + " - " + str(maxX) + "       "
    yReading = "Y: " + str(minY) + " - " + str(maxY) + "       "
        
    display.draw_text(0, 100, xReading, unispace,
                  ili9341.color565(255, 128, 0))
    display.draw_text(0, 125, yReading, unispace,
                  ili9341.color565(255, 128, 0))

display = mySetupX.createMyDisplay()
xptTouch = mySetupX.createXPT(xpt_touch)

print('Loading fonts...')
print('Loading unispace')
unispace = XglcdFont('Unispace12x24.c', 12, 24)

display.draw_text(0, 0, ili9341.__name__, unispace,
                  ili9341.color565(255, 128, 0))
display.draw_text(0, 25, ili9341.implementation.name, unispace,
                  ili9341.color565(0, 0, 200))
display.draw_text(0, 50, str(ili9341.implementation.version), unispace,
                  ili9341.color565(0, 0, 200))

while True:
    pass

print("- bye -")
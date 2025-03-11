from machine import SPI, Pin, I2C
from ili9341 import Display, color565
from time import sleep
import network
import urequests
from xpt2046 import Touch
import asyncio
from xglcd_font import XglcdFont

SPI0_TX = Pin(19)
SPI0_RX = Pin(16)
SPI0_SCK = Pin(18)
SPI0_CSn_right = Pin(17)
SPI0_CSn_left = Pin(1)
SPI0_RESET_right = Pin(20)
SPI0_RESET_left = Pin(2)
SPI0_DC_right = Pin(21)
SPI0_DC_left = Pin(3)

UbuntuMono = XglcdFont('Unispace12x24.c', 12, 24)
arcadepix = XglcdFont('ArcadePix9x11.c', 9, 11)

def main():
    spi = SPI(0, 40_000_000, mosi=SPI0_TX, miso=SPI0_RX, sck=SPI0_SCK)
    display = Display(spi, cs=SPI0_CSn_right, dc=SPI0_DC_right, rst=SPI0_RESET_right)
    display.draw_image('home_layout.raw', 0, 0, 240, 320)
        
    #wifi
    display.draw_image('wifi.raw', 2, 2, 14, 10)
    
    #date
    display.draw_image('zero_tiny_white.raw', 160, 1, 10, 14)
    display.draw_image('zero_tiny_white.raw', 170, 1, 10, 14)
    
    display.draw_image('slash_dark.raw', 180, 1, 10, 14)
    
    display.draw_image('zero_tiny_white.raw', 190, 1, 10, 14)
    display.draw_image('zero_tiny_white.raw', 200, 1, 10, 14)
    
    display.draw_image('slash_dark.raw', 210, 1, 10, 14)
    
    display.draw_image('zero_tiny_white.raw', 220, 1, 10, 14)
    display.draw_image('zero_tiny_white.raw', 230, 1, 10, 14)
    
    #day of week
    #display.draw_text(58, 65, 'Sunday', UbuntuMono, color565(122, 60, 31), background=color565(52, 51, 50))
    display.draw_text(55, 75, 'Sunday', arcadepix, color565(194, 194, 194), background=color565(52, 51, 50))
    
    #time
    display.draw_image('zero_white.raw', 45, 90, 45, 65)
    display.draw_image('zero_white.raw', 95, 90, 45, 65)
    display.draw_image('zero_white.raw', 45, 160, 45, 65)
    display.draw_image('zero_white.raw', 95, 160, 45, 65)
    
    #seconds
    display.draw_image('zero_tiny_white.raw', 53, 230, 10, 14)
    display.draw_image('zero_tiny_white.raw', 65, 230, 10, 14)
    
    #am/pm
    display.draw_text(110, 225, 'AM', UbuntuMono, color565(194, 194, 194), background=color565(52, 51, 50))
    #display.draw_text(113, 233, 'AM', arcadepix, color565(122, 60, 31), background=color565(52, 51, 50))
    
    spi2 = SPI(0, 40_000_000, mosi=SPI0_TX, miso=SPI0_RX, sck=SPI0_SCK)
    display2 = Display(spi2, cs=SPI0_CSn_left, dc=SPI0_DC_left, rst=SPI0_RESET_left)
    display2.draw_image('secondary_screen_layout.raw', 0, 0, 240, 320)
    display2.draw_text(5, 0, 'Green Bay Packers', arcadepix, color565(194, 194, 194), background=color565(52, 51, 50))
    
main()
from machine import SPI, Pin, I2C
from ili9341 import Display, color565
from time import sleep
import network
import urequests
from xpt2046 import Touch
import asyncio

# Pin Configurations

SPI0_TX = Pin(19)
SPI0_RX = Pin(16)
SPI0_SCK = Pin(18)
SPI0_CSn_right = Pin(17)
SPI0_CSn_left = Pin(1)
SPI0_RESET_right = Pin(20)
SPI0_RESET_left = Pin(2)
SPI0_DC_right = Pin(21)
SPI0_DC_left = Pin(3)

T_IRQ = Pin(11)
T_DO = Pin(12)
T_CS = Pin(13)
T_CLK = Pin(14)
T_DI = Pin(15)

I2C_SDA = Pin(8)
I2C_SCL = Pin(9)
I2C_SLAVE_ADDR = 0x68

SECONDARY_SCREEN_TOGGLE = Pin(22, Pin.IN, pull=Pin.PULL_DOWN)
SECONDARY_SCREEN_BACKLIGHT = Pin(26, Pin.OUT)

# Main class to hold all objects

class monk_os():
    def __init__(self, main_display, secondary_display, wifi, clock, apps):
        self.main_display = main_display
        self.secondary_display = secondary_display
        self.wifi = wifi
        self.clock = clock
        
        self.secondary_display_state = False
        self.prev_sec_display_toggle = 0
        self.prev_touch_coords = [0,0]
        
        self.apps = apps
        self.dock_open = False

    async def update_screen(self):
        clock_data = self.clock.read_time()
        self.main_display.update_screen(clock_data)

    async def handle_touch(self):
        touch = self.main_display.touch.raw_touch()
        if touch is not None:
            x,y = self.main_display.touch.normalize(touch[0], touch[1])

            if x <= 120:            
                if not self.dock_open:
                    # home button click
                    if (x <= 60 and x >= 20 and y <= 240 and y >= 130 and (self.prev_touch_coords[0] > 60 or self.prev_touch_coords[0] < 20 and self.prev_touch_coords[1] > 240 or self.prev_touch_coords[1] < 130)):
                        self.open_dock()
                else:
                    # packers button click
                    if (x <= 105 and x >= 60 and y <= 285 and y >= 240 and (self.prev_touch_coords[0] > 105 or self.prev_touch_coords[0] < 60 and self.prev_touch_coords[1] > 285 or self.prev_touch_coords[1] < 240)):
                        print("packers schedule")
                        self.close_dock()
                        self.apps[0].open_app()
                    
                    # brewers button click
                    elif (x <= 105 and x >= 60 and y <= 230 and y >= 135 and (self.prev_touch_coords[0] > 105 or self.prev_touch_coords[0] < 60 and self.prev_touch_coords[1] > 230 or self.prev_touch_coords[1] < 135)):
                        print("brewers schedule")
                        self.close_dock()
                        self.apps[1].open_app()
                        
                    # bucks button click
                    elif (x <= 105 and x >= 60 and y <= 61 and y >= 15 and (self.prev_touch_coords[0] > 105 or self.prev_touch_coords[0] < 60 and self.prev_touch_coords[1] > 61 or self.prev_touch_coords[1] < 15)):
                        print("bucks schedule")
                        self.close_dock()
                        self.apps[2].open_app()
                        
                    # clear secondary screen click
                    elif (x <= 59 and x >= 25 and y <= 285 and y >= 230 and (self.prev_touch_coords[0] > 59 or self.prev_touch_coords[0] < 25 and self.prev_touch_coords[1] > 285 or self.prev_touch_coords[1] < 230)):
                        print("clear screen")
                        self.secondary_display.display.fill_rectangle(0, 0, 240, 320, color565( 218, 193, 144 ))
                        self.secondary_display_state = False
                        self.close_dock()
                        
                    # close dock click
                    elif (x <= 59 and x >= 25 and y <= 230 and y >= 135 and (self.prev_touch_coords[0] > 59 or self.prev_touch_coords[0] < 25 and self.prev_touch_coords[1] > 230 or self.prev_touch_coords[1] < 135)):
                        print("close dock")
                        self.close_dock()
                        
                    # wifi button click
                    elif (x <= 59 and x >= 25 and y <= 63 and y >= 15 and (self.prev_touch_coords[0] > 59 or self.prev_touch_coords[0] < 25 and self.prev_touch_coords[1] > 63 or self.prev_touch_coords[1] < 15)):
                        print('wifi clicked')
                        self.close_dock()
                        if self.wifi.status():
                            await self.wifi.disconnect()
                        else:
                            await self.wifi.connect()
                            for app in self.apps:
                                app.request()
            else:
                self.close_dock()
                    
            self.prev_touch_coords = [x, y]
        else:
            self.prev_touch_coords = [0, 0]
    
    def open_dock(self):
        self.main_display.display.draw_image('app_bar_full.raw', 15, 185, 210, 130)
        self.main_display.display.draw_text8x8(28, 279, 'Clear', color565(0, 0, 0), background=color565(219, 179, 100))
        self.main_display.display.draw_text8x8(176, 279, 'WiFi', color565(0, 0, 0), background=color565(219, 179, 100))
        self.dock_open = True
    
    def close_dock(self):
        self.main_display.display.fill_rectangle(15, 185, 210, 130, color565( 218, 193, 144 ))
        self.main_display.display.draw_image('home_button.raw', 105, 268, 30, 30)
        self.dock_open = False
            
    async def handle_second_screen_on(self):
        button_status = SECONDARY_SCREEN_TOGGLE.value()
        if ((button_status == 1) and (self.prev_sec_display_toggle == 0)):
            if SECONDARY_SCREEN_BACKLIGHT.value() == 1:
                SECONDARY_SCREEN_BACKLIGHT.value(0)
            elif SECONDARY_SCREEN_BACKLIGHT.value() == 0:
                SECONDARY_SCREEN_BACKLIGHT.value(1)
        self.prev_sec_display_toggle = button_status
        
class Main_Display():
    def __init__(self):
        self.spi_display = None
        self.spi_touch = None
        self.display = None
        self.touch = None
        
    def init_screen(self):
        self.spi_display = SPI(0, 40_000_000, mosi=SPI0_TX, miso=SPI0_RX, sck=SPI0_SCK)
        self.display = Display(self.spi_display, cs=SPI0_CSn_right, dc=SPI0_DC_right, rst=SPI0_RESET_right)
        self.display.clear(color565( 218, 193, 144 ))
        self.draw_image('home_button.raw', 105, 268, 30, 30)

    def init_touch(self):
        self.spi_touch = SPI(1, 20_000_000, mosi=T_DI, miso=T_DO, sck=T_CLK)
        self.touch = Touch(self.spi_touch, cs=T_CS, x_min=64, x_max=1847, y_min=148, y_max=2047)
        
    def draw_image(self, image, x, y, width, height):
        self.display.draw_image(image, x, y, width, height)
        
    def update_screen(self, clock_data):
        seconds, ten_seconds, minutes, ten_minutes, hours, ten_hours, AM_PM, day_of_week, day_of_month, ten_day_of_month, month, ten_month, year, ten_year = clock_data
        
        if (seconds == '0x0'):
            self.draw_image('zero_sm.raw', 121, 135, 20, 29)
        elif (seconds == '0x1'):    
            self.draw_image('one_sm.raw', 121, 135, 20, 29)
        elif (seconds == '0x2'):    
            self.draw_image('two_sm.raw', 121, 135, 20, 29)
        elif (seconds == '0x3'):    
            self.draw_image('three_sm.raw', 121, 135, 20, 29)
        elif (seconds == '0x4'):    
            self.draw_image('four_sm.raw', 121, 135, 20, 29)
        elif (seconds == '0x5'):    
            self.draw_image('five_sm.raw', 121, 135, 20, 29)
        elif (seconds == '0x6'):    
            self.draw_image('six_sm.raw', 121, 135, 20, 29)
        elif (seconds == '0x7'):    
            self.draw_image('seven_sm.raw', 121, 135, 20, 29)
        elif (seconds == '0x8'):    
            self.draw_image('eight_sm.raw', 121, 135, 20, 29)
        elif (seconds == '0x9'):    
            self.draw_image('nine_sm.raw', 121, 135, 20, 29)
            
        if (ten_seconds == '0x0'):
            self.draw_image('zero_sm.raw', 100, 135, 20, 29)
        elif (ten_seconds == '0x10'):    
            self.draw_image('one_sm.raw', 100, 135, 20, 29)
        elif (ten_seconds == '0x20'):    
            self.draw_image('two_sm.raw', 100, 135, 20, 29)
        elif (ten_seconds == '0x30'):    
            self.draw_image('three_sm.raw', 100, 135, 20, 29)
        elif (ten_seconds == '0x40'):    
            self.draw_image('four_sm.raw', 100, 135, 20, 29)
        elif (ten_seconds == '0x50'):    
            self.draw_image('five_sm.raw', 100, 135, 20, 29)
        elif (ten_seconds == '0x60'):    
            self.draw_image('six_sm.raw', 100, 135, 20, 29)
        elif (ten_seconds == '0x70'):    
            self.draw_image('seven_sm.raw', 100, 135, 20, 29)
        elif (ten_seconds == '0x80'):    
            self.draw_image('eight_sm.raw', 100, 135, 20, 29)
        elif (ten_seconds == '0x90'):    
            self.draw_image('nine_sm.raw', 100, 135, 20, 29)
                
        if (minutes == '0x0'):
            self.draw_image('zero.raw', 188, 115, 45, 65)
        elif (minutes == '0x1'):    
            self.draw_image('one.raw', 188, 115, 45, 65)
        elif (minutes == '0x2'):    
            self.draw_image('two.raw', 188, 115, 45, 65)
        elif (minutes == '0x3'):    
            self.draw_image('three.raw', 188, 115, 45, 65)
        elif (minutes == '0x4'):    
            self.draw_image('four.raw', 188, 115, 45, 65)
        elif (minutes == '0x5'):    
            self.draw_image('five.raw', 188, 115, 45, 65)
        elif (minutes == '0x6'):    
            self.draw_image('six.raw', 188, 115, 45, 65)
        elif (minutes == '0x7'):    
            self.draw_image('seven.raw', 188, 115, 45, 65)
        elif (minutes == '0x8'):    
            self.draw_image('eight.raw', 188, 115, 45, 65)
        elif (minutes == '0x9'):    
            self.draw_image('nine.raw', 188, 115, 45, 65)
            
        if (ten_minutes == '0x0'):
            self.draw_image('zero.raw', 142, 115, 45, 65)
        elif (ten_minutes == '0x10'):    
            self.draw_image('one.raw', 142, 115, 45, 65)
        elif (ten_minutes == '0x20'):    
            self.draw_image('two.raw', 142, 115, 45, 65)
        elif (ten_minutes == '0x30'):    
            self.draw_image('three.raw', 142, 115, 45, 65)
        elif (ten_minutes == '0x40'):    
            self.draw_image('four.raw', 142, 115, 45, 65)
        elif (ten_minutes == '0x50'):    
            self.draw_image('five.raw', 142, 115, 45, 65)
        elif (ten_minutes == '0x60'):    
            self.draw_image('six.raw', 142, 115, 45, 65)
        elif (ten_minutes == '0x70'):    
            self.draw_image('seven.raw', 142, 115, 45, 65)
        elif (ten_minutes == '0x80'):    
            self.draw_image('eight.raw', 142, 115, 45, 65)
        elif (ten_minutes == '0x90'):    
            self.draw_image('nine.raw', 142, 115, 45, 65)
                
        if (hours == '0x0'):
            self.draw_image('zero.raw', 54, 115, 45, 65)
        elif (hours == '0x1'):    
            self.draw_image('one.raw', 54, 115, 45, 65)
        elif (hours == '0x2'):    
            self.draw_image('two.raw', 54, 115, 45, 65)
        elif (hours == '0x3'):    
            self.draw_image('three.raw', 54, 115, 45, 65)
        elif (hours == '0x4'):    
            self.draw_image('four.raw', 54, 115, 45, 65)
        elif (hours == '0x5'):    
            self.draw_image('five.raw', 54, 115, 45, 65)
        elif (hours == '0x6'):    
            self.draw_image('six.raw', 54, 115, 45, 65)
        elif (hours == '0x7'):    
            self.draw_image('seven.raw', 54, 115, 45, 65)
        elif (hours == '0x8'):    
            self.draw_image('eight.raw', 54, 115, 45, 65)
        elif (hours == '0x9'):    
            self.draw_image('nine.raw', 54, 115, 45, 65)
                
        if (ten_hours == '0x0'):
            self.draw_image('zero.raw', 8, 115, 45, 65)
        elif (ten_hours == '0x10'):    
            self.draw_image('one.raw', 8, 115, 45, 65)
        elif (ten_hours == '0x20'):    
            self.draw_image('two.raw', 8, 115, 45, 65)
        elif (ten_hours == '0x30'):    
            self.draw_image('three.raw', 8, 115, 45, 65)
        elif (ten_hours == '0x40'):    
            self.draw_image('four.raw', 8, 115, 45, 65)
        elif (ten_hours == '0x50'):    
            self.draw_image('five.raw', 8, 115, 45, 65)
        elif (ten_hours == '0x60'):    
            self.draw_image('six.raw', 8, 115, 45, 65)
        elif (ten_hours == '0x70'):    
            self.draw_image('seven.raw', 8, 115, 45, 65)
        elif (ten_hours == '0x80'):    
            self.draw_image('eight.raw', 8, 115, 45, 65)
        elif (ten_hours == '0x90'):    
            self.draw_image('nine.raw', 8, 115, 45, 65)
            
        if (day_of_month == '0x0'):
            self.draw_image('zero_tiny.raw', 121, 5, 10, 14)
        elif (day_of_month == '0x1'):    
            self.draw_image('one_tiny.raw', 121, 5, 10, 14)
        elif (day_of_month == '0x2'):    
            self.draw_image('two_tiny.raw', 121, 5, 10, 14)
        elif (day_of_month == '0x3'):    
            self.draw_image('three_tiny.raw', 121, 5, 10, 14)
        elif (day_of_month == '0x4'):    
            self.draw_image('four_tiny.raw', 121, 5, 10, 14)
        elif (day_of_month == '0x5'):    
            self.draw_image('five_tiny.raw', 121, 5, 10, 14)
        elif (day_of_month == '0x6'):    
            self.draw_image('six_tiny.raw', 121, 5, 10, 14)
        elif (day_of_month == '0x7'):    
            self.draw_image('seven_tiny.raw', 121, 5, 10, 14)
        elif (day_of_month == '0x8'):    
            self.draw_image('eight_tiny.raw', 121, 5, 10, 14)
        elif (day_of_month == '0x9'):    
            self.draw_image('nine_tiny.raw', 121, 5, 10, 14)
            
        if (ten_day_of_month == '0x0'):
            self.draw_image('zero_tiny.raw', 111, 5, 10, 14)
        elif (ten_day_of_month == '0x10'):    
            self.draw_image('one_tiny.raw', 111, 5, 10, 14)
        elif (ten_day_of_month == '0x20'):    
            self.draw_image('two_tiny.raw', 111, 5, 10, 14)
        elif (ten_day_of_month == '0x30'):    
            self.draw_image('three_tiny.raw', 111, 5, 10, 14)
        elif (ten_day_of_month == '0x40'):    
            self.draw_image('four_tiny.raw', 111, 5, 10, 14)
        elif (ten_day_of_month == '0x50'):    
            self.draw_image('five_tiny.raw', 111, 5, 10, 14)
        elif (ten_day_of_month == '0x60'):    
            self.draw_image('six_tiny.raw', 111, 5, 10, 14)
        elif (ten_day_of_month == '0x70'):    
            self.draw_image('seven_tiny.raw', 111, 5, 10, 14)
        elif (ten_day_of_month == '0x80'):    
            self.draw_image('eight_tiny.raw', 111, 5, 10, 14)
        elif (ten_day_of_month == '0x90'):    
            self.draw_image('nine_tiny.raw', 111, 5, 10, 14)
            
        self.draw_image('slash.raw', 101, 5, 10, 14)
        
        if (month == '0x0'):
            self.draw_image('zero_tiny.raw', 90, 5, 10, 14)
        elif (month == '0x1'):    
            self.draw_image('one_tiny.raw', 90, 5, 10, 14)
        elif (month == '0x2'):    
            self.draw_image('two_tiny.raw', 90, 5, 10, 14)
        elif (month == '0x3'):    
            self.draw_image('three_tiny.raw', 90, 5, 10, 14)
        elif (month == '0x4'):    
            self.draw_image('four_tiny.raw', 90, 5, 10, 14)
        elif (month == '0x5'):    
            self.draw_image('five_tiny.raw', 90, 5, 10, 14)
        elif (month == '0x6'):    
            self.draw_image('six_tiny.raw', 90, 5, 10, 14)
        elif (month == '0x7'):    
            self.draw_image('seven_tiny.raw', 90, 5, 10, 14)
        elif (month == '0x8'):    
            self.draw_image('eight_tiny.raw', 90, 5, 10, 14)
        elif (month == '0x9'):    
            self.draw_image('nine_tiny.raw', 90, 5, 10, 14)
            
        if (ten_month == '0x0'):
            self.draw_image('zero_tiny.raw', 80, 5, 10, 14)
        elif (ten_month == '0x10'):    
            self.draw_image('one_tiny.raw', 80, 5, 10, 14)
        elif (ten_month == '0x20'):    
            self.draw_image('two_tiny.raw', 80, 5, 10, 14)
        elif (ten_month == '0x30'):    
            self.draw_image('three_tiny.raw', 80, 5, 10, 14)
        elif (ten_month == '0x40'):    
            self.draw_image('four_tiny.raw', 80, 5, 10, 14)
        elif (ten_month == '0x50'):    
            self.draw_image('five_tiny.raw', 80, 5, 10, 14)
        elif (ten_month == '0x60'):    
            self.draw_image('six_tiny.raw', 80, 5, 10, 14)
        elif (ten_month == '0x70'):    
            self.draw_image('seven_tiny.raw', 80, 5, 10, 14)
        elif (ten_month == '0x80'):    
            self.draw_image('eight_tiny.raw', 80, 5, 10, 14)
        elif (ten_month == '0x90'):    
            self.draw_image('nine_tiny.raw', 80, 5, 10, 14)
            
        self.draw_image('slash.raw', 132, 5, 10, 14)
        
        if (year == '0x0'):
            self.draw_image('zero_tiny.raw', 152, 5, 10, 14)
        elif (year == '0x1'):    
            self.draw_image('one_tiny.raw', 152, 5, 10, 14)
        elif (year == '0x2'):    
            self.draw_image('two_tiny.raw', 152, 5, 10, 14)
        elif (year == '0x3'):    
            self.draw_image('three_tiny.raw', 152, 5, 10, 14)
        elif (year == '0x4'):    
            self.draw_image('four_tiny.raw', 152, 5, 10, 14)
        elif (year == '0x5'):    
            self.draw_image('five_tiny.raw', 152, 5, 10, 14)
        elif (year == '0x6'):    
            self.draw_image('six_tiny.raw', 152, 5, 10, 14)
        elif (year == '0x7'):    
            self.draw_image('seven_tiny.raw', 152, 5, 10, 14)
        elif (year == '0x8'):    
            self.draw_image('eight_tiny.raw', 152, 5, 10, 14)
        elif (year == '0x9'):    
            self.draw_image('nine_tiny.raw', 152, 5, 10, 14)
            
        if (ten_year == '0x0'):
            self.draw_image('zero_tiny.raw', 142, 5, 10, 14)
        elif (ten_year == '0x10'):    
            self.draw_image('one_tiny.raw', 142, 5, 10, 14)
        elif (ten_year == '0x20'):    
            self.draw_image('two_tiny.raw', 142, 5, 10, 14)
        elif (ten_year == '0x30'):    
            self.draw_image('three_tiny.raw', 142, 5, 10, 14)
        elif (ten_year == '0x40'):    
            self.draw_image('four_tiny.raw', 142, 5, 10, 14)
        elif (ten_year == '0x50'):    
            self.draw_image('five_tiny.raw', 142, 5, 10, 14)
        elif (ten_year == '0x60'):    
            self.draw_image('six_tiny.raw', 142, 5, 10, 14)
        elif (ten_year == '0x70'):    
            self.draw_image('seven_tiny.raw', 142, 5, 10, 14)
        elif (ten_year == '0x80'):    
            self.draw_image('eight_tiny.raw', 142, 5, 10, 14)
        elif (ten_year == '0x90'):    
            self.draw_image('nine_tiny.raw', 142, 5, 10, 14)
        
    def draw_bluetooth(self):
        self.draw_image('bluetooth.raw', 225, 5, 10, 14)

    def remove_bluetooth(self):
        self.display.fill_rectangle(225, 5, 10, 14, color565( 218, 193, 144 ))

    def draw_wifi(self):
        self.draw_image('wifi.raw', 205, 6, 14, 10)
        
    def remove_wifi(self):
        self.display.fill_rectangle(205, 6, 14, 10, color565( 218, 193, 144 ))

    def draw_connecting(self):
        self.draw_image('dots.raw', 205, 6, 14, 10)
        
class Secondary_Display():
    def __init__(self):
        self.spi_display = None
        self.display = None
        self.smirk_monk = None
        
    def init_screen(self):
        self.spi_display = SPI(0, 40_000_000, mosi=SPI0_TX, miso=SPI0_RX, sck=SPI0_SCK)
        
        self.display = Display(self.spi_display, cs=SPI0_CSn_left, dc=SPI0_DC_left, rst=SPI0_RESET_left)
        self.display.clear(color565( 218, 193, 144 ))

    def draw_image(self, image, x, y, width, height):
        self.display.draw_image(image, x, y, width, height)
        
class Clock():
    def __init__(self):
        self.i2c_clock = None

    def init_clock(self):
        self.i2c_clock = I2C(0, scl=I2C_SCL, sda=I2C_SDA, freq=100000)

    def start_clock(self):
        self.i2c_clock.writeto(0x68, bytearray([0x0F, 0x8B]))
        
    def stop_clock(self):
        self.i2c_clock.writeto(0x68, bytearray([0x0F, 0x0B]))
    
    def set_time(self):
        self.stop_clock()
        
        #set seconds
        self.i2c_clock.writeto(I2C_SLAVE_ADDR, bytearray([0x00, 0x01]))
        
        #set minutes
        self.i2c_clock.writeto(I2C_SLAVE_ADDR, bytearray([0x01, 0x01]))
        
        #set hours
        self.i2c_clock.writeto(I2C_SLAVE_ADDR, bytearray([0x02, 0x68]))
        
        #set day of week
        self.i2c_clock.writeto(I2C_SLAVE_ADDR, bytearray([0x03, 0x06]))

        #set day of month
        self.i2c_clock.writeto(I2C_SLAVE_ADDR, bytearray([0x04, 0x01]))
        
        #set month
        self.i2c_clock.writeto(I2C_SLAVE_ADDR, bytearray([0x05, 0x03]))
        
        #set year
        self.i2c_clock.writeto(I2C_SLAVE_ADDR, bytearray([0x06, 0x19]))
        
        self.start_clock()
        
        print("Clock set, time started")

    def read_time(self):
        data = self.i2c_clock.readfrom_mem(I2C_SLAVE_ADDR, 0x00, 1)[0]
        seconds = hex(int(data) & 0x0F)
        ten_seconds = hex(int(data) & 0x70)
        
        data = self.i2c_clock.readfrom_mem(I2C_SLAVE_ADDR, 0x01, 1)[0]
        minutes = hex(int(data) & 0x0F)
        ten_minutes = hex(int(data) & 0x70)
        
        
        data = hex(self.i2c_clock.readfrom_mem(I2C_SLAVE_ADDR, 0x02, 1)[0])
        hours = hex(int(data) & 0x0F)
        ten_hours = hex(int(data) & 0x10)
        AM_PM = hex(int(data) & 0x20) # 0x00 AM, 0x20 PM
        
        data = hex(self.i2c_clock.readfrom_mem(I2C_SLAVE_ADDR, 0x03, 1)[0])
        day_of_week = hex(int(data) & 0x07)
        
        data = hex(self.i2c_clock.readfrom_mem(I2C_SLAVE_ADDR, 0x04, 1)[0])
        day_of_month = hex(int(data) & 0x0F)
        ten_day_of_month = hex(int(data) & 0x30)
        
        data = hex(self.i2c_clock.readfrom_mem(I2C_SLAVE_ADDR, 0x05, 1)[0])
        month = hex(int(data) & 0x0F)
        ten_month = hex(int(data) & 0x10)
        
        data = hex(self.i2c_clock.readfrom_mem(I2C_SLAVE_ADDR, 0x06, 1)[0])
        year = hex(int(data) & 0x0F)
        ten_year = hex(int(data) & 0xF0)
        
        return seconds, ten_seconds, minutes, ten_minutes, hours, ten_hours, AM_PM, day_of_week, day_of_month, ten_day_of_month, month, ten_month, year, ten_year

# WiFi Stuff

class WiFi():
    def __init__(self):
        self.wlan = None
        self.socket = None
        self.available_networks = None
        
    def status(self):
        if self.wlan != None:
            return self.wlan.isconnected()
        else:
            return False

    async def connect(self):
        main_os.main_display.draw_connecting()
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        available_networks = self.wlan.scan()
        for available_network in available_networks:
            if available_network[0] == b'NETGEAR60':
                self.wlan.connect('NETGEAR60', 'basictrumpet609')
                
                while self.wlan.isconnected() == False:
                    print('connecting, please wait...')
                    await asyncio.sleep(.5)
                    
                print('connected! ip=', self.wlan.ifconfig()[0])
                main_os.main_display.draw_wifi()
                main_os.secondary_display.display.clear(color565( 218, 193, 144 ))

            elif available_network[0] == b'NETGEAR03':
                self.wlan.connect('NETGEAR03', 'blackkayak533')
                
                while self.wlan.isconnected() == False:
                    print('connecting, please wait...')
                    await asyncio.sleep(.5)
                    
                print('connected! ip=', self.wlan.ifconfig()[0])
                main_os.main_display.draw_wifi()
                main_os.secondary_display.display.clear(color565( 218, 193, 144 ))
   
            elif available_network[0] == b'UWNet':
                self.wlan.connect('UWNet')
                
                while self.wlan.isconnected() == False:
                    print('connecting, please wait...')
                    await asyncio.sleep(.5)
                    
                print('connected! ip=', self.wlan.ifconfig()[0])
                main_os.main_display.draw_wifi()
                main_os.secondary_display.display.clear(color565( 218, 193, 144 ))
                
    async def disconnect(self):
        main_os.main_display.draw_connecting()
        
        self.wlan.disconnect()
        self.wlan.active(False)
        
        while self.wlan.isconnected():
            print("Disconnecting...")
            await asyncio.sleep(.5)
        print("Disconnected")
        
        self.wlan = None
        main_os.main_display.remove_wifi()

class app():
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.resp = None
        self.latest_resp_code = 0
        
    def open_app(self):
        connected = main_os.wifi.status()
        if connected:
            main_os.secondary_display.display.clear(color565( 218, 193, 144 ))
            main_os.secondary_display.display.draw_text8x8(70, 155, 'Loading...', color565(0, 0, 0), background=color565( 218, 193, 144 ))
            self.request()
            self.draw_info()
        elif self.resp != None:
            main_os.secondary_display.display.clear(color565( 218, 193, 144 ))
            self.draw_info()
        else:
            main_os.secondary_display.display.clear(color565( 218, 193, 144 ))
            main_os.secondary_display.display.draw_text8x8(65, 155, 'Not Connected', color565(0, 0, 0), background=color565( 218, 193, 144 ))
    
    def request(self):
        try:
            r = urequests.get(self.endpoint)
            self.resp = r.json()
            self.latest_resp_code = r.status_code
            r.close()
        except OSError as e:
            main_os.secondary_display.display.draw_text8x8(65, 155, 'Request Failed', color565(0, 0, 0), background=color565( 218, 193, 144 ))
    
    def draw_info(self):
        if self.latest_resp_code == 200:
            main_os.secondary_display.display.clear(color565( 218, 193, 144 ))
            for i in range(0, len(self.resp)):
                home_team = self.resp[i]['Home_Team']
                away_team = self.resp[i]['Away_Team']
                home_score = self.resp[i]['Home_Score']
                away_score = self.resp[i]['Away_Score']
                date = self.resp[i]['Date']
                time = self.resp[i]['Time']
                if i == 0:
                    main_os.secondary_display.display.draw_text8x8(15, 10, f"{date} - {time}", color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 20, f"{home_team} - {home_score}", color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 30, 'vs', color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 40, f"{away_team} - {away_score}", color565(0, 0, 0), background=color565(218, 193, 144))
                elif i == 1:
                    main_os.secondary_display.display.draw_text8x8(15, 70, f"{date} - {time}", color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 80, f"{home_team} - {home_score}", color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 90, 'vs', color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 100, f"{away_team} - {away_score}", color565(0, 0, 0), background=color565(218, 193, 144))
                elif i == 2:
                    main_os.secondary_display.display.draw_text8x8(15, 130, f"{date} - {time}", color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 140, f"{home_team} - {home_score}", color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 150, 'vs', color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 160, f"{away_team} - {away_score}", color565(0, 0, 0), background=color565(218, 193, 144))
                elif i == 3:
                    main_os.secondary_display.display.draw_text8x8(15, 190, f"{date} - {time}", color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 200, f"{home_team} - {home_score}", color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 210, 'vs', color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 220, f"{away_team} - {away_score}", color565(0, 0, 0), background=color565(218, 193, 144))
                elif i == 4:
                    main_os.secondary_display.display.draw_text8x8(15, 250, f"{date} - {time}", color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 260, f"{home_team} - {home_score}", color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 270, 'vs', color565(0, 0, 0), background=color565(218, 193, 144))
                    main_os.secondary_display.display.draw_text8x8(15, 280, f"{away_team} - {away_score}", color565(0, 0, 0), background=color565(218, 193, 144))
        elif self.latest_resp_code == 404:
                main_os.secondary_display.display.draw_text8x8(65, 155, 'No Games Found', color565(0, 0, 0), background=color565( 218, 193, 144 ))
    
main_display = Main_Display()
main_display.init_screen()
main_display.init_touch()

secondary_display = Secondary_Display()
secondary_display.init_screen()

clock = Clock()
clock.init_clock()

wifi = WiFi()

packers_app = app('https://rrrrlgrot7knkm7twzqzfi6cda0mepib.lambda-url.us-east-2.on.aws/')
brewers_app = app('https://qgk63yzapnm7q7i7jefehuopkm0xnwro.lambda-url.us-east-2.on.aws/')
bucks_app = app('https://6puu43kgcctatxxjax6dew5p7u0tjpaf.lambda-url.us-east-2.on.aws/')

global main_os
main_os = monk_os(main_display, secondary_display, wifi, clock, [packers_app, brewers_app, bucks_app])

async def task_update_screen():
    while True:
        await main_os.update_screen()
        await asyncio.sleep(.3)

async def task_touch():
    while True:
        await main_os.handle_touch()
        await asyncio.sleep(.2)
        
async def task_sec_display_toggle():
    while True:
        await main_os.handle_second_screen_on()
        await asyncio.sleep(.2)

async def main_scheduler():
    # Create async tasks
    await asyncio.gather(
        asyncio.create_task(task_update_screen()),
        asyncio.create_task(task_touch()),
        asyncio.create_task(task_sec_display_toggle())
    )

asyncio.run(main_scheduler())
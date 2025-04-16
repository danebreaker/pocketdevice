from machine import SPI, Pin, I2C
from ili9341 import Display, color565
from time import sleep
import network
import urequests
from xpt2046 import Touch
import asyncio
from xglcd_font import XglcdFont
import time

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

#T_IRQ = Pin(11)
T_DO = Pin(12)
T_CS = Pin(13)
T_CLK = Pin(14)
T_DI = Pin(15)

T2_CS = Pin(10)

I2C_SDA = Pin(8)
I2C_SCL = Pin(9)
I2C_SLAVE_ADDR = 0x68

SECONDARY_SCREEN_TOGGLE = Pin(22, Pin.IN, pull=Pin.PULL_DOWN)
SECONDARY_SCREEN_BACKLIGHT = Pin(26, Pin.OUT)

UbuntuMono = XglcdFont('Unispace12x24.c', 12, 24)
arcadepix = XglcdFont('ArcadePix9x11.c', 9, 11)

# Main class to hold all objects

class monk_os():
    def __init__(self, main_display, secondary_display, wifi, clock, apps):
        self.main_display = main_display
        self.secondary_display = secondary_display
        self.wifi = wifi
        self.clock = clock
        
        self.secondary_display_state = False
        self.prev_sec_display_toggle = 0
        self.prev_touch_coords = [0]
        
        self.apps = apps
        self.shown_apps = []
        self.open_app = None
        self.apps_bar_index = 0
        
        self.update_apps_bar()

    async def update_screen(self):
        clock_data = self.clock.read_time()
        self.main_display.update_screen(clock_data)     

    def update_apps_bar(self):
        self.shown_apps = self.apps[self.apps_bar_index:self.apps_bar_index+3]

        self.main_display.draw_image(self.shown_apps[0].icon, 189, 80, 46, 46)
        self.main_display.draw_image(self.shown_apps[1].icon, 189, 146, 46, 46)
        self.main_display.draw_image(self.shown_apps[2].icon, 189, 212, 46, 46)

    async def handle_touch(self):
        touch = self.main_display.touch.raw_touch()
        touch2 = self.secondary_display.touch.raw_touch()
        #print(touch2)
        if touch is not None:
            x,y = touch
#             print(x,y)
            
            if (y <= 511 and y >= 255 and (self.prev_touch_coords[1] > 511 or self.prev_touch_coords[1] < 255)):
                if (x <= 1616 and x >= 1568 and (self.prev_touch_coords[0] > 1616 or self.prev_touch_coords[0] < 1568)):
                    print("up arrow")
                    if self.apps_bar_index != 0:
                        self.apps_bar_index -= 1
                        self.update_apps_bar()
                     
                elif (x <= 255 and x >= 127 and (self.prev_touch_coords[0] > 255 or self.prev_touch_coords[0] < 127)):
                    print("down arrow")
                    if self.apps_bar_index != len(self.apps) - 3:
                        self.apps_bar_index += 1
                        self.update_apps_bar()
                
                # top app click
                elif (x <= 1536 and x >= 1120 and (self.prev_touch_coords[0] > 1536 or self.prev_touch_coords[0] < 1120)):
                    print("app 1 clicked")
                    if self.open_app:
                        self.open_app.close_app()
                        
                    app_type = str(type(self.shown_apps[0]))[8:12]
                    if (app_type == 'wifi'):
                        await self.shown_apps[0].open_app()
                    else:
                        self.shown_apps[0].open_app()
                    self.open_app = self.shown_apps[0]
                
                # middle app click
                elif (x <= 1008 and x >= 832 and (self.prev_touch_coords[0] > 1008 or self.prev_touch_coords[0] < 832)):
                    print("app 2 clicked")
                    if self.open_app:
                        self.open_app.close_app()
                        
                    app_type = str(type(self.shown_apps[1]))[8:12]
                    if (app_type == 'wifi'):
                        await self.shown_apps[1].open_app()
                    else:
                        self.shown_apps[1].open_app()
                    self.open_app = self.shown_apps[1]
            
                #bottom app click
                elif (x <= 800 and x >= 496 and (self.prev_touch_coords[0] > 800 or self.prev_touch_coords[0] < 496)):
                    print("app 3 clicked")
                    if self.open_app:
                        self.open_app.close_app()
                     
                    app_type = str(type(self.shown_apps[2]))[8:12]
                    if (app_type == 'wifi'):
                        await self.shown_apps[2].open_app()
                    else:
                        self.shown_apps[2].open_app()
                    self.open_app = self.shown_apps[2]
                
            else:
                await self.load_data()
                    
            self.prev_touch_coords = [x, y]
        else:
            self.prev_touch_coords = [0, 0]
    
            
    async def handle_second_screen_on(self):
        button_status = SECONDARY_SCREEN_TOGGLE.value()
        if ((button_status == 1) and (self.prev_sec_display_toggle == 0)):
            if SECONDARY_SCREEN_BACKLIGHT.value() == 1:
                SECONDARY_SCREEN_BACKLIGHT.value(0)
            elif SECONDARY_SCREEN_BACKLIGHT.value() == 0:
                SECONDARY_SCREEN_BACKLIGHT.value(1)
        self.prev_sec_display_toggle = button_status
        
        
    def write_cache(self, file, data):
        cached_sched = open(file, 'w')
        cached_sched.write(str(data))
        cached_sched.close()
        self.secondary_display.display.draw_text8x8(65, 155, 'All Data Loaded', color565(194, 194, 194), background=color565( 52, 51, 50 ))
        
        
    async def load_data(self):
        await self.wifi.connect()
        for app in self.apps:
            print(app.app_name)
            try:
                if app.endpoint != None:
                    app.request()
                    self.write_cache(app.file_name, app.resp)
            except:
                pass
        
class Main_Display():
    def __init__(self):
        self.spi_display = None
        self.spi_touch = None
        self.display = None
        self.touch = None
        
    def init_screen(self):
        self.spi_display = SPI(0, 40_000_000, mosi=SPI0_TX, miso=SPI0_RX, sck=SPI0_SCK)
        self.display = Display(self.spi_display, cs=SPI0_CSn_right, dc=SPI0_DC_right, rst=SPI0_RESET_right)
        self.draw_image('home_layout.raw', 0, 0, 240, 320)

    def init_touch(self):
        self.spi_touch = SPI(1, 20_000_000, mosi=T_DI, miso=T_DO, sck=T_CLK)
        self.touch = Touch(self.spi_touch, cs=T_CS, x_min=127, x_max=1888, y_min=255, y_max=1888)
        #self.touch = Touch(self.spi_touch, cs=T_CS)
        
    def draw_image(self, image, x, y, width, height):
        self.display.draw_image(image, x, y, width, height)
        
    def update_screen(self, clock_data):
        seconds, ten_seconds, minutes, ten_minutes, hours, ten_hours, AM_PM, day_of_week, day_of_month, ten_day_of_month, month, ten_month, year, ten_year = clock_data
        
        if (day_of_week == '0x1'):
            self.display.draw_text(55, 75, 'Monday', arcadepix, color565(194, 194, 194), background=color565(52, 51, 50))
        elif (day_of_week == '0x2'):
            self.display.draw_text(55, 75, 'Tuesday', arcadepix, color565(194, 194, 194), background=color565(52, 51, 50))
        elif (day_of_week == '0x3'):
            self.display.draw_text(55, 75, 'Wednesday', arcadepix, color565(194, 194, 194), background=color565(52, 51, 50))
        elif (day_of_week == '0x4'):
            self.display.draw_text(55, 75, 'Thursday', arcadepix, color565(194, 194, 194), background=color565(52, 51, 50))
        elif (day_of_week == '0x5'):
            self.display.draw_text(55, 75, 'Friday', arcadepix, color565(194, 194, 194), background=color565(52, 51, 50))
        elif (day_of_week == '0x6'):
            self.display.draw_text(55, 75, 'Saturday', arcadepix, color565(194, 194, 194), background=color565(52, 51, 50))
        elif (day_of_week == '0x7'):
            self.display.draw_text(55, 75, 'Sunday', arcadepix, color565(194, 194, 194), background=color565(52, 51, 50))
        
        
        if (AM_PM == '0x20'):
            self.display.draw_text(110, 225, 'PM', UbuntuMono, color565(194, 194, 194), background=color565(52, 51, 50))
        else:
            self.display.draw_text(110, 225, 'AM', UbuntuMono, color565(194, 194, 194), background=color565(52, 51, 50))
        
        if (seconds == '0x0'):
            self.draw_image('zero_sm.raw', 65, 230, 10, 14)
        elif (seconds == '0x1'):    
            self.draw_image('one_sm.raw', 65, 230, 10, 14)
        elif (seconds == '0x2'):    
            self.draw_image('two_sm.raw', 65, 230, 10, 14)
        elif (seconds == '0x3'):    
            self.draw_image('three_sm.raw', 65, 230, 10, 14)
        elif (seconds == '0x4'):    
            self.draw_image('four_sm.raw', 65, 230, 10, 14)
        elif (seconds == '0x5'):    
            self.draw_image('five_sm.raw', 65, 230, 10, 14)
        elif (seconds == '0x6'):    
            self.draw_image('six_sm.raw', 65, 230, 10, 14)
        elif (seconds == '0x7'):    
            self.draw_image('seven_sm.raw', 65, 230, 10, 14)
        elif (seconds == '0x8'):    
            self.draw_image('eight_sm.raw', 65, 230, 10, 14)
        elif (seconds == '0x9'):    
            self.draw_image('nine_sm.raw', 65, 230, 10, 14)
            
        if (ten_seconds == '0x0'):
            self.draw_image('zero_sm.raw', 53, 230, 10, 14)
        elif (ten_seconds == '0x10'):    
            self.draw_image('one_sm.raw', 53, 230, 10, 14)
        elif (ten_seconds == '0x20'):    
            self.draw_image('two_sm.raw', 53, 230, 10, 14)
        elif (ten_seconds == '0x30'):    
            self.draw_image('three_sm.raw', 53, 230, 10, 14)
        elif (ten_seconds == '0x40'):    
            self.draw_image('four_sm.raw', 53, 230, 10, 14)
        elif (ten_seconds == '0x50'):    
            self.draw_image('five_sm.raw', 53, 230, 10, 14)
        elif (ten_seconds == '0x60'):    
            self.draw_image('six_sm.raw', 53, 230, 10, 14)
        elif (ten_seconds == '0x70'):    
            self.draw_image('seven_sm.raw', 53, 230, 10, 14)
        elif (ten_seconds == '0x80'):    
            self.draw_image('eight_sm.raw', 53, 230, 10, 14)
        elif (ten_seconds == '0x90'):    
            self.draw_image('nine_sm.raw', 53, 230, 10, 14)
                
        if (minutes == '0x0'):
            self.draw_image('zero.raw', 95, 160, 45, 65)
        elif (minutes == '0x1'):    
            self.draw_image('one.raw', 95, 160, 45, 65)
        elif (minutes == '0x2'):    
            self.draw_image('two.raw', 95, 160, 45, 65)
        elif (minutes == '0x3'):    
            self.draw_image('three.raw', 95, 160, 45, 65)
        elif (minutes == '0x4'):    
            self.draw_image('four.raw', 95, 160, 45, 65)
        elif (minutes == '0x5'):    
            self.draw_image('five.raw', 95, 160, 45, 65)
        elif (minutes == '0x6'):    
            self.draw_image('six.raw', 95, 160, 45, 65)
        elif (minutes == '0x7'):    
            self.draw_image('seven.raw', 95, 160, 45, 65)
        elif (minutes == '0x8'):    
            self.draw_image('eight.raw', 95, 160, 45, 65)
        elif (minutes == '0x9'):    
            self.draw_image('nine.raw', 95, 160, 45, 65)
            
        if (ten_minutes == '0x0'):
            self.draw_image('zero.raw', 45, 160, 45, 65)
        elif (ten_minutes == '0x10'):    
            self.draw_image('one.raw', 45, 160, 45, 65)
        elif (ten_minutes == '0x20'):    
            self.draw_image('two.raw', 45, 160, 45, 65)
        elif (ten_minutes == '0x30'):    
            self.draw_image('three.raw', 45, 160, 45, 65)
        elif (ten_minutes == '0x40'):    
            self.draw_image('four.raw', 45, 160, 45, 65)
        elif (ten_minutes == '0x50'):    
            self.draw_image('five.raw', 45, 160, 45, 65)
        elif (ten_minutes == '0x60'):    
            self.draw_image('six.raw', 45, 160, 45, 65)
        elif (ten_minutes == '0x70'):    
            self.draw_image('seven.raw', 45, 160, 45, 65)
        elif (ten_minutes == '0x80'):    
            self.draw_image('eight.raw', 45, 160, 45, 65)
        elif (ten_minutes == '0x90'):    
            self.draw_image('nine.raw', 45, 160, 45, 65)
                
        if (hours == '0x0'):
            self.draw_image('zero.raw', 95, 90, 45, 65)
        elif (hours == '0x1'):    
            self.draw_image('one.raw', 95, 90, 45, 65)
        elif (hours == '0x2'):    
            self.draw_image('two.raw', 95, 90, 45, 65)
        elif (hours == '0x3'):    
            self.draw_image('three.raw', 95, 90, 45, 65)
        elif (hours == '0x4'):    
            self.draw_image('four.raw', 95, 90, 45, 65)
        elif (hours == '0x5'):    
            self.draw_image('five.raw', 95, 90, 45, 65)
        elif (hours == '0x6'):    
            self.draw_image('six.raw', 95, 90, 45, 65)
        elif (hours == '0x7'):    
            self.draw_image('seven.raw', 95, 90, 45, 65)
        elif (hours == '0x8'):    
            self.draw_image('eight.raw', 95, 90, 45, 65)
        elif (hours == '0x9'):    
            self.draw_image('nine.raw', 95, 90, 45, 65)
                
        if (ten_hours == '0x0'):
            self.draw_image('zero.raw', 45, 90, 45, 65)
        elif (ten_hours == '0x10'):    
            self.draw_image('one.raw', 45, 90, 45, 65)
        elif (ten_hours == '0x20'):    
            self.draw_image('two.raw', 45, 90, 45, 65)
        elif (ten_hours == '0x30'):    
            self.draw_image('three.raw', 45, 90, 45, 65)
        elif (ten_hours == '0x40'):    
            self.draw_image('four.raw', 45, 90, 45, 65)
        elif (ten_hours == '0x50'):    
            self.draw_image('five.raw', 45, 90, 45, 65)
        elif (ten_hours == '0x60'):    
            self.draw_image('six.raw', 45, 90, 45, 65)
        elif (ten_hours == '0x70'):    
            self.draw_image('seven.raw', 45, 90, 45, 65)
        elif (ten_hours == '0x80'):    
            self.draw_image('eight.raw', 45, 90, 45, 65)
        elif (ten_hours == '0x90'):    
            self.draw_image('nine.raw', 45, 90, 45, 65)
            
        if (day_of_month == '0x0'):
            self.draw_image('zero_sm_dark.raw', 200, 1, 10, 14)
        elif (day_of_month == '0x1'):    
            self.draw_image('one_sm_dark.raw', 200, 1, 10, 14)
        elif (day_of_month == '0x2'):    
            self.draw_image('two_sm_dark.raw', 200, 1, 10, 14)
        elif (day_of_month == '0x3'):    
            self.draw_image('three_sm_dark.raw', 200, 1, 10, 14)
        elif (day_of_month == '0x4'):    
            self.draw_image('four_sm_dark.raw', 200, 1, 10, 14)
        elif (day_of_month == '0x5'):    
            self.draw_image('five_sm_dark.raw', 200, 1, 10, 14)
        elif (day_of_month == '0x6'):    
            self.draw_image('six_sm_dark.raw', 200, 1, 10, 14)
        elif (day_of_month == '0x7'):    
            self.draw_image('seven_sm_dark.raw', 200, 1, 10, 14)
        elif (day_of_month == '0x8'):    
            self.draw_image('eight_sm_dark.raw', 200, 1, 10, 14)
        elif (day_of_month == '0x9'):    
            self.draw_image('nine_sm_dark.raw', 200, 1, 10, 14)
            
        if (ten_day_of_month == '0x0'):
            self.draw_image('zero_sm_dark.raw', 190, 1, 10, 14)
        elif (ten_day_of_month == '0x10'):    
            self.draw_image('one_sm_dark.raw', 190, 1, 10, 14)
        elif (ten_day_of_month == '0x20'):    
            self.draw_image('two_sm_dark.raw', 190, 1, 10, 14)
        elif (ten_day_of_month == '0x30'):    
            self.draw_image('three_sm_dark.raw', 190, 1, 10, 14)
        elif (ten_day_of_month == '0x40'):    
            self.draw_image('four_sm_dark.raw', 190, 1, 10, 14)
        elif (ten_day_of_month == '0x50'):    
            self.draw_image('five_sm_dark.raw', 190, 1, 10, 14)
        elif (ten_day_of_month == '0x60'):    
            self.draw_image('six_sm_dark.raw', 190, 1, 10, 14)
        elif (ten_day_of_month == '0x70'):    
            self.draw_image('seven_sm_dark.raw', 190, 1, 10, 14)
        elif (ten_day_of_month == '0x80'):    
            self.draw_image('eight_sm_dark.raw', 190, 1, 10, 14)
        elif (ten_day_of_month == '0x90'):    
            self.draw_image('nine_sm_dark.raw', 190, 1, 10, 14)
            
        self.draw_image('slash.raw', 180, 1, 10, 14)
        
        if (month == '0x0'):
            self.draw_image('zero_sm_dark.raw', 170, 1, 10, 14)
        elif (month == '0x1'):    
            self.draw_image('one_sm_dark.raw', 170, 1, 10, 14)
        elif (month == '0x2'):    
            self.draw_image('two_sm_dark.raw', 170, 1, 10, 14)
        elif (month == '0x3'):    
            self.draw_image('three_sm_dark.raw', 170, 1, 10, 14)
        elif (month == '0x4'):    
            self.draw_image('four_sm_dark.raw', 170, 1, 10, 14)
        elif (month == '0x5'):    
            self.draw_image('five_sm_dark.raw', 170, 1, 10, 14)
        elif (month == '0x6'):    
            self.draw_image('six_sm_dark.raw', 170, 1, 10, 14)
        elif (month == '0x7'):    
            self.draw_image('seven_sm_dark.raw', 170, 1, 10, 14)
        elif (month == '0x8'):    
            self.draw_image('eight_sm_dark.raw', 170, 1, 10, 14)
        elif (month == '0x9'):    
            self.draw_image('nine_sm_dark.raw', 170, 1, 10, 14)
            
        if (ten_month == '0x0'):
            self.draw_image('zero_sm_dark.raw', 160, 1, 10, 14)
        elif (ten_month == '0x10'):    
            self.draw_image('one_sm_dark.raw', 160, 1, 10, 14)
        elif (ten_month == '0x20'):    
            self.draw_image('two_sm_dark.raw', 160, 1, 10, 14)
        elif (ten_month == '0x30'):    
            self.draw_image('three_sm_dark.raw', 160, 1, 10, 14)
        elif (ten_month == '0x40'):    
            self.draw_image('four_sm_dark.raw', 160, 1, 10, 14)
        elif (ten_month == '0x50'):    
            self.draw_image('five_sm_dark.raw', 160, 1, 10, 14)
        elif (ten_month == '0x60'):    
            self.draw_image('six_sm_dark.raw', 160, 1, 10, 14)
        elif (ten_month == '0x70'):    
            self.draw_image('seven_sm_dark.raw', 160, 1, 10, 14)
        elif (ten_month == '0x80'):    
            self.draw_image('eight_sm_dark.raw', 160, 1, 10, 14)
        elif (ten_month == '0x90'):    
            self.draw_image('nine_sm_dark.raw', 160, 1, 10, 14)
            
        self.draw_image('slash.raw', 210, 1, 10, 14)
        
        if (year == '0x0'):
            self.draw_image('zero_sm_dark.raw', 230, 1, 10, 14)
        elif (year == '0x1'):    
            self.draw_image('one_sm_dark.raw', 230, 1, 10, 14)
        elif (year == '0x2'):    
            self.draw_image('two_sm_dark.raw', 230, 1, 10, 14)
        elif (year == '0x3'):    
            self.draw_image('three_sm_dark.raw', 230, 1, 10, 14)
        elif (year == '0x4'):    
            self.draw_image('four_sm_dark.raw', 230, 1, 10, 14)
        elif (year == '0x5'):    
            self.draw_image('five_sm_dark.raw', 230, 1, 10, 14)
        elif (year == '0x6'):    
            self.draw_image('six_sm_dark.raw', 230, 1, 10, 14)
        elif (year == '0x7'):    
            self.draw_image('seven_sm_dark.raw', 230, 1, 10, 14)
        elif (year == '0x8'):    
            self.draw_image('eight_sm_dark.raw', 230, 1, 10, 14)
        elif (year == '0x9'):    
            self.draw_image('nine_sm_dark.raw', 230, 1, 10, 14)
            
        if (ten_year == '0x0'):
            self.draw_image('zero_sm_dark.raw', 220, 1, 10, 14)
        elif (ten_year == '0x10'):    
            self.draw_image('one_sm_dark.raw', 220, 1, 10, 14)
        elif (ten_year == '0x20'):    
            self.draw_image('two_sm_dark.raw', 220, 1, 10, 14)
        elif (ten_year == '0x30'):    
            self.draw_image('three_sm_dark.raw', 220, 1, 10, 14)
        elif (ten_year == '0x40'):    
            self.draw_image('four_sm_dark.raw', 220, 1, 10, 14)
        elif (ten_year == '0x50'):    
            self.draw_image('five_sm_dark.raw', 220, 1, 10, 14)
        elif (ten_year == '0x60'):    
            self.draw_image('six_sm_dark.raw', 220, 1, 10, 14)
        elif (ten_year == '0x70'):    
            self.draw_image('seven_sm_dark.raw', 220, 1, 10, 14)
        elif (ten_year == '0x80'):    
            self.draw_image('eight_sm_dark.raw', 220, 1, 10, 14)
        elif (ten_year == '0x90'):    
            self.draw_image('nine_sm_dark.raw', 220, 1, 10, 14)
        
    # def draw_bluetooth(self):
    #     self.draw_image('bluetooth.raw', 225, 5, 10, 14)

    # def remove_bluetooth(self):
    #     self.display.fill_rectangle(225, 5, 10, 14, color565( 218, 193, 144 ))

    def draw_wifi(self):
        self.draw_image('wifi.raw', 2, 2, 14, 10)
        
    def remove_wifi(self):
        self.display.fill_rectangle(2, 2, 14, 10, color565( 37, 36, 34 ))

    def draw_connecting(self):
        self.draw_image('dots.raw', 2, 2, 14, 10)
        
class Secondary_Display():
    def __init__(self):
        self.spi_display = None
        self.spi_touch = None
        self.touch = None
        self.display = None
        self.smirk_monk = None
        
    def init_screen(self):
        self.spi_display = SPI(0, 40_000_000, mosi=SPI0_TX, miso=SPI0_RX, sck=SPI0_SCK)
        
        self.display = Display(self.spi_display, cs=SPI0_CSn_left, dc=SPI0_DC_left, rst=SPI0_RESET_left)
        self.draw_image('secondary_screen_layout.raw', 0, 0, 240, 320)
        
    def init_touch(self):
        self.spi_touch = SPI(1, 20_000_000, mosi=T_DI, miso=T_DO, sck=T_CLK)
        self.touch = Touch(self.spi_touch, cs=T2_CS, x_min=127, x_max=1888, y_min=255, y_max=1888)

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

            elif available_network[0] == b'NETGEAR03':
                self.wlan.connect('NETGEAR03', 'blackkayak533')
                
                while self.wlan.isconnected() == False:
                    print('connecting, please wait...')
                    await asyncio.sleep(.5)
                    
                print('connected! ip=', self.wlan.ifconfig()[0])
                main_os.main_display.draw_wifi()
   
            elif available_network[0] == b'UWNet':
                self.wlan.connect('UWNet')
                
                while self.wlan.isconnected() == False:
                    print('connecting, please wait...')
                    await asyncio.sleep(.5)
                    
                print('connected! ip=', self.wlan.ifconfig()[0])
                main_os.main_display.draw_wifi()
                
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

class schedule_app():
    def __init__(self, app_name, icon, file_name, endpoint=None):
        self.app_name = app_name
        self.endpoint = endpoint
        self.icon = icon
        self.file_name = file_name
        self.resp = None
        self.latest_resp_code = 0
        
    def open_app(self):
        print(self.app_name)
        main_os.secondary_display.display.draw_text(5, 2, self.app_name, arcadepix, color565(194, 194, 194), background=color565(37, 36, 34))
        connected = main_os.wifi.status()
        if connected:
            main_os.secondary_display.display.draw_text8x8(70, 155, 'Loading...', color565(194, 194, 194), background=color565( 52, 51, 50 ))
            self.request()
            self.draw_info()
            self.write_cache()
        elif self.resp != None:
            self.draw_info()
        else:
            main_os.secondary_display.display.draw_text8x8(65, 155, 'Not Connected', color565(194, 194, 194), background=color565( 52, 51, 50 ))
    
    def close_app(self):
        main_os.secondary_display.display.draw_image('secondary_screen_layout.raw', 0, 0, 240, 320)
    
    def request(self):
        try:
            r = urequests.get(self.endpoint)
            self.resp = r.json()
            self.latest_resp_code = r.status_code
            r.close()
        except OSError as e:
            main_os.secondary_display.display.draw_text8x8(65, 155, 'Request Failed', color565(194, 194, 194), background=color565( 52, 51, 50 ))
    
    def draw_info(self):
        if self.latest_resp_code == 200:
#TODO
#clear middle box
            for i in range(0, len(self.resp)):
                home_team = self.resp[i]['Home_Team']
                away_team = self.resp[i]['Away_Team']
                home_score = self.resp[i]['Home_Score']
                away_score = self.resp[i]['Away_Score']
                date = time.localtime(self.resp[i]['Date'])
                if i == 0:
                    main_os.secondary_display.display.draw_text8x8(15, 25, f"{date[1]}/{date[2]}/{date[0]} - {date[3] + 2}:{date[4]:02d}", color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 35, f"{home_team} - {home_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 45, 'vs', color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 55, f"{away_team} - {away_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                elif i == 1:
                    main_os.secondary_display.display.draw_text8x8(15, 85, f"{date[1]}/{date[2]}/{date[0]} - {date[3] + 2}:{date[4]:02d}", color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 95, f"{home_team} - {home_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 105, 'vs', color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 115, f"{away_team} - {away_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                elif i == 2:
                    main_os.secondary_display.display.draw_text8x8(15, 145, f"{date[1]}/{date[2]}/{date[0]} - {date[3] + 2}:{date[4]:02d}", color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 155, f"{home_team} - {home_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 165, 'vs', color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 175, f"{away_team} - {away_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                elif i == 3:
                    main_os.secondary_display.display.draw_text8x8(15, 205, f"{date[1]}/{date[2]}/{date[0]} - {date[3] + 2}:{date[4]:02d}", color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 215, f"{home_team} - {home_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 225, 'vs', color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 235, f"{away_team} - {away_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                elif i == 4:
                    main_os.secondary_display.display.draw_text8x8(15, 265, f"{date[1]}/{date[2]}/{date[0]} - {date[3] + 2}:{date[4]:02d}", color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 275, f"{home_team} - {home_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 285, 'vs', color565(194, 194, 194), background=color565(52, 51, 50))
                    main_os.secondary_display.display.draw_text8x8(15, 295, f"{away_team} - {away_score}", color565(194, 194, 194), background=color565(52, 51, 50))
        elif self.latest_resp_code == 404:
                main_os.secondary_display.display.draw_text8x8(65, 155, 'No Games Found', color565(194, 194, 194), background=color565( 52, 51, 50 ))
    
    def write_cache(self):
        if self.resp != None:
            cached_sched = open(self.file_name, 'w')
            cached_sched.write(str("test"))
            cached_sched.close()
        
    
class wifi_app():
    def __init__(self, app_name, icon, wifi):
        self.app_name = app_name
        self.icon = icon
        self.wifi = wifi
        
    async def open_app(self):
        if self.wifi.status():
            await self.wifi.disconnect()
        else:
            await self.wifi.connect()
    
    def close_app(self):
        main_os.secondary_display.display.draw_image('secondary_screen_layout.raw', 0, 0, 240, 320)
        
        
class clear_sec_screen_app():
    def __init__(self, app_name, icon,sec_display):
        self.app_name = app_name
        self.icon = icon
        self.secondary_display = sec_display
        
    def open_app(self):
        self.secondary_display.display.draw_image('secondary_screen_layout.raw', 0, 0, 240, 320)
    
    def close_app(self):
        self.secondary_display.display.draw_image('secondary_screen_layout.raw', 0, 0, 240, 320)
    
        
main_display = Main_Display()
main_display.init_screen()
main_display.init_touch()

secondary_display = Secondary_Display()
secondary_display.init_screen()
secondary_display.init_touch()

clock = Clock()
clock.init_clock()

wifi = WiFi()

packers_app = schedule_app('Packers Schedule', 'packers_app_icon.raw', 'packers_sched_cache.csv', 'https://rrrrlgrot7knkm7twzqzfi6cda0mepib.lambda-url.us-east-2.on.aws/')
brewers_app = schedule_app('Brewers Schedule', 'brewers_app_icon.raw', 'brewers_sched_cache.csv', 'http://192.168.1.3:8000/brewers/')
bucks_app = schedule_app('Bucks Schedule',  'bucks_app_icon.raw', 'bucks_sched_cache.csv', 'https://6puu43kgcctatxxjax6dew5p7u0tjpaf.lambda-url.us-east-2.on.aws/')
badgers_app = schedule_app('Badgers Schedule', 'badgers_app_icon.raw', 'badgers_sched_cache.csv', 'https://rrrrlgrot7knkm7twzqzfi6cda0mepib.lambda-url.us-east-2.on.aws/')
f1_app = schedule_app('Formula 1 Schedule', 'f1_app_icon.raw', 'f1_sched_cache.csv', 'https://rrrrlgrot7knkm7twzqzfi6cda0mepib.lambda-url.us-east-2.on.aws/')

settings_app = wifi_app('WiFi', 'settings_app_icon.raw', wifi)
clear_sec_screen_app = clear_sec_screen_app('Clear Screen', 'clear_app_icon.raw', secondary_display)

global main_os
main_os = monk_os(main_display, secondary_display, wifi, clock, [packers_app, brewers_app, bucks_app, badgers_app, f1_app, settings_app, clear_sec_screen_app])

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
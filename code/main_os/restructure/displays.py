from externals import main_display, secondary_display, touch_main, touch_sec
from xglcd_font import XglcdFont
from ili9341 import color565
from machine import Pin

SECONDARY_SCREEN_BACKLIGHT = Pin(26, Pin.OUT)

Unispace = XglcdFont('Unispace12x24.c', 12, 24)
arcadepix = XglcdFont('ArcadePix9x11.c', 9, 11)

class Main_Display():
    def __init__(self):
        self.display = main_display
        self.touch = touch_main
        self.draw_image('home_layout.raw', 0, 0, 240, 320)
        
    def draw_image(self, image, x, y, width, height):
        self.display.draw_image(image, x, y, width, height)
        
    def update_time(self, clock_data):
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
            self.display.draw_text(110, 225, 'PM', Unispace, color565(194, 194, 194), background=color565(52, 51, 50))
        else:
            self.display.draw_text(110, 225, 'AM', Unispace, color565(194, 194, 194), background=color565(52, 51, 50))
        
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
        self.display = secondary_display
        self.touch = touch_sec
        self.screen_on = False
        self.draw_image('secondary_screen_layout.raw', 0, 0, 240, 320)     

    def draw_image(self, image, x, y, width, height):
        self.display.draw_image(image, x, y, width, height)
        
    def toggle_screen(self):
        if SECONDARY_SCREEN_BACKLIGHT.value() == 1:
            SECONDARY_SCREEN_BACKLIGHT.value(0)
        elif SECONDARY_SCREEN_BACKLIGHT.value() == 0:
            SECONDARY_SCREEN_BACKLIGHT.value(1)
            
    def clear_info(self):
        self.display.fill_rectangle(15, 25, 15, 310, color565( 52, 51, 50 ))
        
    def close_app(self):
        self.draw_image('secondary_screen_layout.raw', 0, 0, 240, 320)
from ili9341 import color565
import time
from time import sleep
import urequests
import asyncio
from xglcd_font import XglcdFont
from machine import Pin

from clock import Clock
from wifi import WiFi
from displays import Main_Display, Secondary_Display
from brewers_app import Brewers_App

arcadepix = XglcdFont('ArcadePix9x11.c', 9, 11)

SECONDARY_SCREEN_TOGGLE = Pin(22, Pin.IN)

# Main class to hold all objects
class monk_os():
    def __init__(self, main_display, secondary_display, wifi, clock, apps):
        self.main_display = main_display
        self.secondary_display = secondary_display
        self.wifi = wifi
        self.clock = clock
        
        self.prev_sec_display_toggle = 0
        self.prev_touch_coords = [0]
        
        self.apps = apps
        self.shown_apps = []
        self.open_app = None
        self.apps_bar_index = 0
        
        self.update_time()
        self.update_apps_bar()

    async def update_time(self):
        clock_data = self.clock.read_time()
        self.main_display.update_time(clock_data)     

    def update_apps_bar(self):
        self.shown_apps = self.apps[self.apps_bar_index:self.apps_bar_index+3]

        self.main_display.draw_image(self.shown_apps[0].icon, 189, 80, 46, 46)
        self.main_display.draw_image(self.shown_apps[1].icon, 189, 146, 46, 46)
        self.main_display.draw_image(self.shown_apps[2].icon, 189, 212, 46, 46)

    async def handle_touch(self):
        touch = self.main_display.touch.raw_touch()
#         print(touch)
#         touch2 = self.secondary_display.touch.raw_touch()
#         print(touch2)
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
                
#             else:
#                 await self.load_data()
                    
            self.prev_touch_coords = [x, y]
        else:
            self.prev_touch_coords = [0, 0]
    
            
    async def handle_second_screen_on(self):
        button_status = SECONDARY_SCREEN_TOGGLE.value()
        
        # button pushed
        if ((button_status == 1) and (self.prev_sec_display_toggle == 0)):
            self.secondary_display.toggle_screen()
            
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
    def __init__(self, wifi, main_display, secondary_display):
        self.app_name = 'WiFi'
        self.icon = 'settings_app_icon.raw'
        self.wifi = wifi
        self.main_display = main_display
        self.secondary_display = secondary_display
        
    async def open_app(self):
        if self.wifi.status():
            main_display.draw_connecting()
            if await self.wifi.disconnect():
                main_display.remove_wifi()
        else:
            main_display.draw_connecting()
            if await self.wifi.connect():
                main_display.draw_wifi()
            else:
                main_display.remove_wifi()
    
    def close_app(self):
        self.secondary_display.close_app()
        
        
class clear_sec_screen_app():
    def __init__(self, secondary_display):
        self.app_name = 'Clear Screen'
        self.icon = 'clear_app_icon.raw'
        self.secondary_display = secondary_display
        
    def open_app(self):
        self.secondary_display.close_app()
        
    def close_app(self):
        self.secondary_display.close_app()
    
        
main_display = Main_Display()
secondary_display = Secondary_Display()
clock = Clock()
wifi = WiFi()

# packers_app = schedule_app('Packers Schedule', 'packers_app_icon.raw', 'packers_sched_cache.csv', 'https://rrrrlgrot7knkm7twzqzfi6cda0mepib.lambda-url.us-east-2.on.aws/')
# brewers_app = schedule_app('Brewers Schedule', 'brewers_app_icon.raw', 'brewers_sched_cache.csv', 'http://192.168.1.3:8000/brewers/')
# bucks_app = schedule_app('Bucks Schedule',  'bucks_app_icon.raw', 'bucks_sched_cache.csv', 'https://6puu43kgcctatxxjax6dew5p7u0tjpaf.lambda-url.us-east-2.on.aws/')
# badgers_app = schedule_app('Badgers Schedule', 'badgers_app_icon.raw', 'badgers_sched_cache.csv', 'https://rrrrlgrot7knkm7twzqzfi6cda0mepib.lambda-url.us-east-2.on.aws/')
# f1_app = schedule_app('Formula 1 Schedule', 'f1_app_icon.raw', 'f1_sched_cache.csv', 'https://rrrrlgrot7knkm7twzqzfi6cda0mepib.lambda-url.us-east-2.on.aws/')

settings_app = wifi_app(wifi, main_display, secondary_display)
clear_sec_screen_app = clear_sec_screen_app(secondary_display)

brewers_app = Brewers_App(main_display, secondary_display, wifi)

global main_os
main_os = monk_os(main_display, secondary_display, wifi, clock, [brewers_app, settings_app, clear_sec_screen_app])

async def task_update_screen():
    while True:
        await main_os.update_time()
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
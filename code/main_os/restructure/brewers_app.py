import urequests
from xglcd_font import XglcdFont
from ili9341 import color565
import time

arcadepix = XglcdFont('ArcadePix9x11.c', 9, 11)

class Brewers_App():
    def __init__(self, main_display, secondary_display, wifi):
        self.app_name = 'Brewers Schedule'
        self.endpoint = 'http://192.168.1.3:8000/brewers/'
        self.icon = 'brewers_app_icon.raw'
        self.file_name = 'brewers_sched_cache.csv'
        self.main_display = main_display
        self.secondary_display = secondary_display
        self.wifi = wifi
        self.resp = None
        self.latest_resp_code = 0
        
    def open_app(self):
        self.secondary_display.display.draw_text(5, 2, self.app_name, arcadepix, color565(194, 194, 194), background=color565(37, 36, 34))
        connected = self.wifi.status()
        if connected:
            self.secondary_display.display.draw_text8x8(70, 155, 'Loading...', color565(194, 194, 194), background=color565( 52, 51, 50 ))
            self.request()
            self.draw_info()
            self.write_cache()
        elif self.resp != None:
            self.draw_info()
        else:
            self.secondary_display.display.draw_text8x8(65, 155, 'Not Connected', color565(194, 194, 194), background=color565( 52, 51, 50 ))
    
    def close_app(self):
        self.secondary_display.close_app()
    
    def request(self):
        try:
            r = urequests.get(self.endpoint)
            self.resp = r.json()
            self.latest_resp_code = r.status_code
            r.close()
        except OSError as e:
            self.secondary_display.display.draw_text8x8(65, 155, 'Request Failed', color565(194, 194, 194), background=color565( 52, 51, 50 ))
    
    def draw_info(self):
        if self.latest_resp_code == 200:
            self.secondary_display.clear_info()
            for i in range(0, len(self.resp)):
                home_team = self.resp[i]['Home_Team']
                away_team = self.resp[i]['Away_Team']
                home_score = self.resp[i]['Home_Score']
                away_score = self.resp[i]['Away_Score']
                date = time.localtime(self.resp[i]['Date'])
                if i == 0:
                    self.secondary_display.display.draw_text8x8(15, 25, f"{date[1]}/{date[2]}/{date[0]} - {date[3] + 2}:{date[4]:02d}", color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 35, f"{home_team} - {home_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 45, 'vs', color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 55, f"{away_team} - {away_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                elif i == 1:
                    self.secondary_display.display.draw_text8x8(15, 85, f"{date[1]}/{date[2]}/{date[0]} - {date[3] + 2}:{date[4]:02d}", color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 95, f"{home_team} - {home_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 105, 'vs', color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 115, f"{away_team} - {away_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                elif i == 2:
                    self.secondary_display.display.draw_text8x8(15, 145, f"{date[1]}/{date[2]}/{date[0]} - {date[3] + 2}:{date[4]:02d}", color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 155, f"{home_team} - {home_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 165, 'vs', color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 175, f"{away_team} - {away_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                elif i == 3:
                    self.secondary_display.display.draw_text8x8(15, 205, f"{date[1]}/{date[2]}/{date[0]} - {date[3] + 2}:{date[4]:02d}", color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 215, f"{home_team} - {home_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 225, 'vs', color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 235, f"{away_team} - {away_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                elif i == 4:
                    self.secondary_display.display.draw_text8x8(15, 265, f"{date[1]}/{date[2]}/{date[0]} - {date[3] + 2}:{date[4]:02d}", color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 275, f"{home_team} - {home_score}", color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 285, 'vs', color565(194, 194, 194), background=color565(52, 51, 50))
                    self.secondary_display.display.draw_text8x8(15, 295, f"{away_team} - {away_score}", color565(194, 194, 194), background=color565(52, 51, 50))
        elif self.latest_resp_code == 404:
                self.secondary_display.display.draw_text8x8(65, 155, 'No Games Found', color565(194, 194, 194), background=color565( 52, 51, 50 ))
    
    def write_cache(self):
        if self.resp != None:
            cached_sched = open(self.file_name, 'w')
            cached_sched.write(str("test"))
            cached_sched.close()
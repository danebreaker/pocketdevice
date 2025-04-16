from externals import i2c_clock

I2C_SLAVE_ADDR = 0x68

class Clock():
    def __init__(self):
        self.i2c_clock = i2c_clock

    def start_clock(self):
        self.i2c_clock.writeto(I2C_SLAVE_ADDR, bytearray([0x0F, 0x8B]))
        
    def stop_clock(self):
        self.i2c_clock.writeto(I2C_SLAVE_ADDR, bytearray([0x0F, 0x0B]))
    
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

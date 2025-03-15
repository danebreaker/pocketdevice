from machine import SPI, Pin, I2C
from ili9341 import Display, color565
from time import sleep

I2C_SDA = Pin(8)
I2C_SCL = Pin(9)
I2C_SLAVE_ADDR = 0x68

i2c = I2C(0, scl=I2C_SCL, sda=I2C_SDA, freq=100000)

def start_clock(i2c):
    i2c.writeto(0x68, bytearray([0x0F, 0x8B]))
    
def stop_clock(i2c):
    i2c.writeto(0x68, bytearray([0x0F, 0x0B]))
    
stop_clock(i2c)

#set seconds
i2c.writeto(I2C_SLAVE_ADDR, bytearray([0x00, 0x01]))

#set minutes
i2c.writeto(I2C_SLAVE_ADDR, bytearray([0x01, 0x38]))

#set hours
i2c.writeto(I2C_SLAVE_ADDR, bytearray([0x02, 0x67]))

#set day of week
i2c.writeto(I2C_SLAVE_ADDR, bytearray([0x03, 0x05]))

#set day of month
i2c.writeto(I2C_SLAVE_ADDR, bytearray([0x04, 0x14]))

#set month
i2c.writeto(I2C_SLAVE_ADDR, bytearray([0x05, 0x03]))

#set year
i2c.writeto(I2C_SLAVE_ADDR, bytearray([0x06, 0x25]))

start_clock(i2c)

print("Clock set, time started")

from machine import SPI, Pin, I2C
from ili9341 import Display
from xpt2046 import Touch

# Pin Definitions
SPI0_TX = Pin(19)
SPI0_RX = Pin(16)
SPI0_SCK = Pin(18)
SPI0_CSn_Main = Pin(17)
SPI0_CSn_Sec = Pin(1)
SPI0_RESET_Main = Pin(20)
SPI0_RESET_Sec = Pin(2)
SPI0_DC_Main = Pin(21)
SPI0_DC_Sec = Pin(3)

T_DO = Pin(12)
T_DI = Pin(15)
T_CLK = Pin(14)

T_CS_Main = Pin(13)
T_CS_Sec = Pin(10)

I2C_SDA = Pin(8)
I2C_SCL = Pin(9)
I2C_SLAVE_ADDR = 0x68

# Device Configuration
# Display
spi_display = SPI(0, 40_000_000, mosi=SPI0_TX, miso=SPI0_RX, sck=SPI0_SCK)
spi_touch = SPI(1, 20_000_000, mosi=T_DI, miso=T_DO, sck=T_CLK)

main_display = Display(spi_display, cs=SPI0_CSn_Main, dc=SPI0_DC_Main, rst=SPI0_RESET_Main)
secondary_display = Display(spi_display, cs=SPI0_CSn_Sec, dc=SPI0_DC_Sec, rst=SPI0_RESET_Sec)

touch_main = Touch(spi_touch, cs=T_CS_Main, x_min=127, x_max=1888, y_min=255, y_max=1888)
touch_sec = Touch(spi_touch, cs=T_CS_Sec, x_min=127, x_max=1888, y_min=255, y_max=1888)

# Clock Module
i2c_clock = I2C(0, scl=I2C_SCL, sda=I2C_SDA, freq=100000)
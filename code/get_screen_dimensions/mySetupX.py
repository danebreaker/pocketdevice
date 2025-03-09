from ili9341 import Display
from machine import Pin, SPI
from xpt2046 import Touch

TFT_CLK_PIN = const(18)
TFT_MOSI_PIN = const(19)
TFT_MISO_PIN = const(16)

TFT_CS_PIN = const(17)
TFT_RST_PIN = const(20)
TFT_DC_PIN = const(21)

XPT_CLK_PIN = const(14)
XPT_MOSI_PIN = const(15)
XPT_MISO_PIN = const(12)

XPT_CS_PIN = const(13)
XPT_INT = const(11)

def createMyDisplay():
    spiTFT = SPI(0, baudrate=40000000, sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN))
    display = Display(spiTFT,
                      dc=Pin(TFT_DC_PIN), cs=Pin(TFT_CS_PIN), rst=Pin(TFT_RST_PIN))
    return display

def createXPT(touch_handler):
    spiXPT = SPI(1, baudrate=1000000,
                 sck=Pin(XPT_CLK_PIN), mosi=Pin(XPT_MOSI_PIN), miso=Pin(XPT_MISO_PIN))

    xpt = Touch(spiXPT, cs=Pin(XPT_CS_PIN), int_pin=Pin(XPT_INT),
                int_handler=touch_handler)

    return xpt
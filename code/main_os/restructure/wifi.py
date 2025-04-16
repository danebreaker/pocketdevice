import network
import asyncio

class WiFi():
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.available_networks = None
        
    def status(self):
        return self.wlan.isconnected()

    async def connect(self):
        self.wlan.active(True)
        
        available_networks = self.wlan.scan()
        for available_network in available_networks:
            network_name = available_network[0]
            if network_name == b'NETGEAR60':
                self.wlan.connect('NETGEAR60', 'basictrumpet609')
                
                while self.wlan.isconnected() == False:
                    print('connecting, please wait...')
                    await asyncio.sleep(.5)
                    
                print('connected! ip=', self.wlan.ifconfig()[0])
                return True

            elif network_name == b'NETGEAR03':
                self.wlan.connect('NETGEAR03', 'blackkayak533')
                
                while self.wlan.isconnected() == False:
                    print('connecting, please wait...')
                    await asyncio.sleep(.5)
                    
                print('connected! ip=', self.wlan.ifconfig()[0])
                return True
   
            elif network_name == b'UWNet':
                self.wlan.connect('UWNet')
                
                while self.wlan.isconnected() == False:
                    print('connecting, please wait...')
                    await asyncio.sleep(.5)
                    
                print('connected! ip=', self.wlan.ifconfig()[0])
                return True
        
        return False
                
    async def disconnect(self):
        self.wlan.disconnect()
        self.wlan.active(False)
        
        while self.wlan.isconnected():
            print("Disconnecting...")
            await asyncio.sleep(.5)
        print("Disconnected")
        
        return True
import time  
import asyncio
import playground
#import re

class clientProtocol(asyncio.Protocol):
    def __init__(self,loop):
        self.loop = loop
        self.message = 'RESULT,'
        self.recv = ""
        #self.loop = loop
        #self.transport = None
        self.session = 0
    
    def connection_made(self,transport):
        self.transport = transport
        self.transport.write("<EOL>\n".encode())
            
    def data_received(self,data):
        self.recv = data.decode()
        print(self.recv)
        #message = "SUBMIT,{ziyang lin},{zlin32@jh,edu},{2},{54216}"
        
        self.message = self.message + input()
        self.transport.write(self.message.encode())
        print(self.message)
        
            
        #self.transport.close()


    
'''

async def main(loop):
    message = "SUBMIT,{ziyang lin},{zlin32@jh,edu},{2},{54216}<EOL>\n"
    transport,protocol = await loop.create_connection(
        lambda: clientProtocol(message,loop),'192.168.200.52',19003)
    
    message = "look mirror<EOL>\nget hairpin<EOL>\nunlock door with hairpin<EOL>\nopen door<EOL>\n"
    #print(transport.data)
    transport.write(message.encode())
'''      
if __name__=="__main__":
    loop = asyncio.get_event_loop()    
    coro = playground.create_connection(lambda:clientProtocol(loop),'20194.0.0.19000',19005)
    loop.run_until_complete(coro)
    try:
        loop.run_forever()
	
    except KeyboardInterrupt:
        pass

    loop.close()
 

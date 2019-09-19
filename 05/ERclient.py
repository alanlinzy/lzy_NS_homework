import time  
import asyncio
#import re

class clientProtocol(asyncio.Protocol):
    def __init__(self,loop):
        self.loop = loop
        self.message = ['SUBMIT,ziyang lin,zlin32@jh.edu,2,54219',
                        'look mirror<EOL>\n',
                        'get hairpin<EOL>\n',
                        'unlock chest with hairpin<EOL>\n',
                        'open chest<EOL>\n',
                        'get hammer from chest<EOL>\n',
                        'hit flyingkey with hammer<EOL>\n',
                        "get key<EOL>\n"
                        'unlock door with key<EOL>\n',
                        'open door<EOL>\n']
        self.recv = ""
        #self.loop = loop
        #self.transport = None
        self.session = 0
    
    def connection_made(self,transport):
        self.transport = transport
        self.transport.write('<EOL>/n')
            
    def data_received(self,data):
        self.recv = data.decode().replace('<EOL>\n','')
        print(self.recv)
        #message = "SUBMIT,{ziyang lin},{zlin32@jh,edu},{2},{54216}"
        
        if self.session <10 and self.session !=6:
            self.transport.write(self.message[self.session].encode())
            print(self.message[self.session])
            #if self.recv.split(' ')[-1] != "wall":
            self.session += 1
        elif self.session ==6:
            if self.recv.split(' ')[-1] == "wall":
                self.transport.write(self.message[self.session].encode())
                print(self.message[self.session])
                self.session += 1
            else:
                pass
            
            
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
    coro = loop.create_connection(lambda:clientProtocol(loop),'20194.0.0.19000',19005)
    loop.run_until_complete(coro)
    try:
        loop.run_forever()
	
    except KeyboardInterrupt:
        pass

    loop.close()
 

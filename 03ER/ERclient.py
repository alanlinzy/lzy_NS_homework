import socket
import time  
import asyncio
import re

class clientProtocol(asyncio.Protocol):
    def __init__(self):
        #self.message = message
        self.recv = ""
        #self.loop = loop
        #self.transport = None
    
    def connection_made(self,transport):
        self.transport = transport
        message = "SUBMIT,{ziyang lin},{zlin32@jh,edu},{2},{54216}"
        self.transport.write(message.encode())
        respon = re.search(r"OK",self.recv)
        print(respon)
        if respon:
            message = "look mirror<EOL>\nget hairpin<EOL>\nunlock door with hairpin<EOL>\nopen door<EOL>\n"
            self.transport.write(message.encode())
            #print(self.message)
        else:
            print('fail')
            
    def data_received(self,data):
        self.recv = data.decode()
        print(self.recv)
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
    coro = loop.create_connection(clientProtocol,'127.0.0.1',54216)
    client = loop.run_until_complete(coro)

    try:
        loop.run_forever()
	
    except KeyboardInterrupt:
        pass

    client.close()
    loop.run_until_complete(client.close())
    loop.close()
 

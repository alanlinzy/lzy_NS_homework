import socket
import time  
import asyncio

class clientProtocol(asyncio.Protocol):
    def __init__(self,message,loop):
        self.message = message

        self.loop = loop
        self.transport = None
    
    def connection_made(self,transport):
        self.transport = transport

        #self.transport.write(self.message.encode())
        #print(self.message)
            
    def data_received(self,data):
        print(data.decode())
        self.transport.close()

    def connection_lost(self,exc):

        self.loop.stop()
    


async def main(loop):
    message = ""
    transport,protocol = await loop.create_connection(
        lambda: clientProtocol(message,loop),'192.168.200.52',19003)
    info = "SUBMIT,{ziyang lin},{zlin32@jh,edu},{2},{54216}<EOL>\n"
    message = "look mirror<EOL>\nget hairpin<EOL>\nunlock door with hairpin<EOL>\nopen door<EOL>\n"
    transport.write(info.encode())
    time.sleep(0.5)
    #print(transport.data)
    transport.write(message.encode())
        
if __name__=="__main__":
    loop = asyncio.get_event_loop()    
    
    loop.run_until_complete(main(loop))
    #loop.run_forever()
    loop.close()
   

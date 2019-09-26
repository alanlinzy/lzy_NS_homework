import time  
import asyncio
import playground
import autograder
import gamepacket
from playground.network.packet import PacketType
#import re

class clientProtocol(asyncio.Protocol):
    def __init__(self,loop):
        self.loop = loop
        self.name = "ziyang lin"
        self.email = "zlin32@jh.edu"
        self.team = "2"
        self.port ="4219"
        self.packet_file=b""
        self.deserializer = PacketType.Deserializer()
        self.message = ['look mirror',
                        'get hairpin',
                        'unlock chest with hairpin',
                        'open chest',
                        'get hammer from chest',
                        'hit flyingkey with hammer',
                        "get key"
                        'unlock door with key',
                        'open door']
        #self.recv = ""
        #self.loop = loop
        #self.transport = None
        self.session = 0
        self.commpkt = gamepacket.GameCommandPacket()
    
    def connection_made(self,transport):
        self.transport = transport
        self.packeconnect = autograder.AutogradeStartTest(name=self.name,
                                                          email=self.email,
                                                          team=self.team,
                                                          port=self.port)
        with open("my_packet_file.py", "rb") as f:
            self.packeconnect.packet_file = f.read()
        
        self.transport.write(self.packeconnect.__serialize__())
            
    def data_received(self,data):
        self.deserializer.update(data)
        print(self.deserializer.update(data))
        for pk in self.deserializer.nextPackets():
            print(pk)
            if pk.DEFINITION_IDENTIFIER == autograder.AutogradeTestStatus.DEFINITION_IDENTIFIER:
                print(pk.test_id)
                if pk.submit_status != autograder.AutogradeTestStatus.PASSED:
                    print(pk.error)
            elif pk.DEFINITION_IDENTIFIER == gamepacket.GameResponsePacket.DEFINITION_IDENTIFIER:
                 if self.session <9 and self.session !=5:
                     self.send_gamepacket()
                 elif self.session ==5:
                     if pk.gameresponse.split(" ")[-1] == "wall":
                         self.send_gamepacket()
                     else:
                         pass
    def send_gamepacket(self):
        self.commpkt.gamecommand = self.message[self.session]
        self.transport.write(self.commpkt.__serialize__())
        print(self.message[self.session])
        self.session += 1
                
'''       
        self.recv = data.decode().replace('<EOL>\n','')
        print(self.recv)
        
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
    coro = playground.create_connection(lambda:clientProtocol(loop),'20194.0.0.19000',19006)
    loop.run_until_complete(coro)
    try:
        loop.run_forever()
	
    except KeyboardInterrupt:
        pass

    loop.close()
 

import time  
import asyncio
import playground
import autograder
import gamepacket
from playground.network.packet import PacketType
from playground.common.logging import EnablePresetLogging, PRESET_VERBOSE
EnablePresetLogging(PRESET_VERBOSE)
#import re

class clientProtocol(asyncio.Protocol):
    def __init__(self,loop):
        self.loop = loop
        self.recv = ""
        #self.loop = loop
        #self.transport = None
        self.result = autograder.AutogradeResultRequest()
        self.response = autograder.AutogradeResultResponse()
        self.deserializer = PacketType.Deserializer()
        self.session = 0
        self.testid = ""
    
    def connection_made(self,transport):
        self.transport = transport
        self.testid = input()
        self.result.test_id = self.testid
        self.transport.write(self.result.__serialize__())
        print("send")
            
    def data_received(self,data):
        self.deserializer.update(data)
        print(self.deserializer.update(data))
        for pk in self.deserializer.nextPackets():
            if pk.DEFINITION_IDENTIFIER == "20194.exercise6.autograderesultresponse":
                print(pk.test_id)
                print(pk.passed)
            else:
                print("what's that?")

            


    
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
 

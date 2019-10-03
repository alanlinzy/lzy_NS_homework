import sys
sys.path.insert( 1,'../Bank/src/')
sys.path.insert( 1,'../Bank/test/')
import time  
import asyncio
import getpass
import playground
import autograder
import gamepacket
import bank_hello_world as bhw
from OnlineBank import BankClientProtocol, OnlineBankConfig
from playground.network.packet import PacketType
from playground.common.logging import EnablePresetLogging, PRESET_VERBOSE
EnablePresetLogging(PRESET_VERBOSE)
#import re

class clientProtocol(asyncio.Protocol):
    def __init__(self,loop):
        self.loop = loop
        self.name = "ziyang lin"
        self.email = "zlin32@jh.edu"
        self.team = "2"
        self.port ="4240"
        self.packet_file=b""
        self.deserializer = PacketType.Deserializer()
        self.message = ['look mirror',
                        'get hairpin',
                        'unlock chest with hairpin',
                        'open chest',
                        'get hammer from chest',
                        'hit flyingkey with hammer',
                        "get key",
                        'unlock door with key',
                        'open door']
        #self.recv = ""
        #self.loop = loop
        #self.transport = None
        self.session = 0
        self.commpkt = gamepacket.GameCommandPacket()
        self.unique_id = ""
        self.username = "zlin32"
        self.src_account = "zlin32_account"
        self.dst_account = ""
        self.payment = 0
        self.receipt =""
        self.receipt_sig =""
    
    def connection_made(self,transport):
        self.transport = transport
        self.packeconnect = autograder.AutogradeStartTest(name=self.name,
                                                          email=self.email,
                                                          team=self.team,
                                                          port=self.port)
        
        self.transport.write(self.packeconnect.__serialize__())
        print("sendpacket")
            
    def data_received(self,data):
        print("client")
        self.deserializer.update(data)
        #print(self.deserializer.update(data))
        for pk in self.deserializer.nextPackets():
            print(pk)
            if pk.DEFINITION_IDENTIFIER == autograder.AutogradeTestStatus.DEFINITION_IDENTIFIER:
                print(pk.test_id)
                print(pk.submit_status)
                print(pk.client_status)
                print(pk.server_status)
                print(pk.error)
                stop = input()
                if pk.submit_status == autograder.AutogradeTestStatus.PASSED :
                    print("create init")
                    startpacket = gamepacket.create_game_init_packet(self.username)
                    self.transport.write(startpacket.__serialize__())
                else:
                    print("no success create init")

            elif pk.DEFINITION_IDENTIFIER == gamepacket.GameRequirePayPacket.DEFINITION_IDENTIFIER:
                print(pk.unique_id)
                print(pk.account)
                print(pk.amount)
                self.unique_id = pk.unique_id #memo
                self.dst_account = pk.account
                self.payment = int(pk.amount)
                password = "qq1997lzy0509"#getpass.getpass("Enter password for {}: ".format(username))
                bank_client = BankClientProtocol(bhw.bank_cert, self.username, password)
                print("trying connect bank")
                loop = asyncio.get_event_loop()
    
                task = loop.create_task(
                       bhw.example_transfer(bank_client, self.src_account, self.dst_account, self.payment, self.unique_id))
                task.add_done_callback(self.finish)
                '''
                if result:
                    print("get receipt")
                    receipt = result.Receipt
                    receipt_signature= result.ReceiptSignature
                    print(receipt)
                    print(receipt_signature)
                    receipt_packet = create_game_pay_packet(receipt,receipt_signature)
                    self.transport.write(receipt_packet.__serialize__())
                    print("send receipt!")
                    #bhw.example_verify(bank_client, result.Receipt, result.ReceiptSignature, dst, amount, memo)
                    #print("Receipt verified.")

                #create_game_require_pay_packet
                #get receipt
                '''
            elif pk.DEFINITION_IDENTIFIER == gamepacket.GameResponsePacket.DEFINITION_IDENTIFIER:
                 #print(pk.gameover)
                 #self.printpacket(pk)
                 #print(pk.status())
                 print(pk.response)
                 if self.session <9 and self.session !=5:
                     self.send_gamepacket()
                 elif self.session ==5:
                     if pk.response.split(" ")[-1] == "wall":
                         self.send_gamepacket()
                     else:
                         pass
            else:
                for field in pkt.FIELDS:
                    fname = field[0]
                    print(fname +str(pkt._fields[fname]._data))
                print("what's that?")
                
    def send_gamepacket(self):
        self.commpkt.command = self.message[self.session]
        self.transport.write(self.commpkt.__serialize__())
        print(self.message[self.session])
        self.session += 1

    def finish(self,task):
        print("function")
        print(task)
        result = task.result()
        try:
            print("sent payment")
            receipt = result.Receipt
            receipt_signature= result.ReceiptSignature
            print(receipt)
            print(receipt_signature)
            receipt_packet = gamepacket.create_game_pay_packet(receipt,receipt_signature)
            self.transport.write(receipt_packet.__serialize__())
            print("send receipt!")
        except Exception as e:
            print("payment fail")
            print(e)
            
    def printpacket(self,pk):
         for f in pk.FIELDS:
             fname = f[0]
             print(fname + str(pk._fields[fname]._data))
             print("\n")
                
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
    coro = playground.create_connection(lambda:clientProtocol(loop),'20194.0.0.19000',19008)
    loop.run_until_complete(coro)
    try:
        loop.run_forever()
	
    except KeyboardInterrupt:
        pass

    loop.close()
 

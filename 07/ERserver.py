import sys
sys.path.insert( 1,'../Bank/src/')
sys.path.insert( 1,'../Bank/test/')
import time
import getpass
import asyncio
import playground
import autograder
import gamepacket
import bank_hello_world as bhw
from OnlineBank import BankClientProtocol, OnlineBankConfig
from playground.network.packet import PacketType
from playground.common.logging import EnablePresetLogging, PRESET_VERBOSE
EnablePresetLogging(PRESET_VERBOSE)
#import re

class myserver(asyncio.Protocol):
   
    def connection_made(self,transport):
        peername = transport.get_extra_info("peername")
        print(peername)
        self.transport = transport
        self.deserializer = PacketType.Deserializer()
        self.responsepkt = gamepacket.GameResponsePacket()
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(asyncio.wait([asyncio.ensure_future(a) for a in self.game.agents])) 
        self.unique_id ="doaiuafavnriuu"
        self.account ="zlin32_account"
        self.username = "zlin32"
        self.permit = 0
        self.payment = 10

    def startgame(self):
        self.game = ERM.EscapeRoomGame(output = self.write_func)
        self.game.create_game(cheat=True)
        self.game.start()
        
    def write_func(self,message):
        #socket.send()
        print(message)
        self.responsepkt = gamepacket.GameResponsePacket(response_string=message,
                                                         status_string =self.game.status)
        #self.responsepkt.gameover = self.responsepkt.game_over()
        print(self.responsepkt.status())
        print(self.responsepkt.game_over())
        #self.responsepkt.gameresponse = message
        self.transport.write(self.responsepkt.__serialize__())
        
    
    def data_received(self,data):
        print("server")
        self.deserializer.update(data)
        #print(self.deserializer.update(data))
        for pk in self.deserializer.nextPackets():
            print(pk)
            if pk.DEFINITION_IDENTIFIER == autograder.AutogradeTestStatus.DEFINITION_IDENTIFIER:
                print(pk.test_id)
                if pk.submit_status != autograder.AutogradeTestStatus.PASSED:
                    print(pk.submit_status)
                    print(pk.client_status)
                    print(pk.server_status)
                    print(pk.error)
            elif pk.DEFINITION_IDENTIFIER == gamepacket.GameInitRequest.DEFINITION_IDENTIFIER:
                print("game init")
                self.clientname = gamepacket.process_game_init(pk)
                print("sent payment request")
                requestpk = gamepacket.create_game_require_pay_packet(self.unique_id, self,account, self.payment)
                self.transport.write(requestpk.__serialize__())

            elif pk.DEFINITION_IDENTIFIER == gamepacket.GamePaymentResponse.DEFINITION_IDENTIFIER:
                print("game response")
                password =  getpass.getpass("Enter password for {}: ".format(username))
                bank_client = BankClientProtocol(bhw.bank_cert, self.username, password)
                receipt = process_game_pay_packet(pk)
                if bhw.example_verify(bank_client, receipt[0], receipt[1], self.account, self.payment, self.unique_id)
                    print("Receipt verified.")
                    self.startgame()
                else:
                    print("bad receipt")
                    bad_receipt_pk = gamepacket.create_game_response("","dead")
                    self.transport.write(bad_receipt_pk.__serialize__())
            elif pk.DEFINITION_IDENTIFIER == gamepacket.GameCommandPacket.DEFINITION_IDENTIFIE:
                 print("playing game")
                 if self.game.status == "playing":
                     print(pk.command_string)
                     output = self.game.command(pk.command_string)
            else:
                print("what's that")
        '''
        if self.game.status == "playing":
            #command = input(">> ")
            #self.conn.send(b'>>')
            data = message# this could be multiple messages
            data_as_string = data.decode() # convert from bytes to string
            lines = data_as_string.split("<EOL>\n")
            print(lines)
            for line in lines:
                print(line)
                if line !="":
                    # process each line
                    command = line
                    output = self.game.command(command)
                
        else:
            self.transport.close()
        '''
        
if __name__=="__main__":
    loop = asyncio.get_event_loop()
    # Each client connection will create a new protocol instance
    c = playground.create_server(myserver,'localhost',4226)
    server = loop.run_until_complete(c)

    # Serve requests until Ctrl+C is pressed
    #print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
   


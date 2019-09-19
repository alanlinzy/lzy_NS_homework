
import time  
import ERM05
import asyncio
import playground

class myserver(asyncio.Protocol):
   
    def connection_made(self,transport):
        peername = transport.get_extra_info("peername")
        print(peername)
        self.transport = transport
        self.game = ERM04.EscapeRoomGame(output = self.write_func)
        self.game.create_game(cheat=True)
        self.game.start()
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(asyncio.wait([asyncio.ensure_future(a) for a in self.game.agents]))
        
    def write_func(self,message):
        #socket.send()
        self.transport.write(message.encode())
        print(message)
    
    def data_received(self,message):
        print(message.decode())
        #print(s.recv(1024))
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
        
        
if __name__=="__main__":
    loop = asyncio.get_event_loop()
    # Each client connection will create a new protocol instance
    c = playground.create_server(myserver,'localhost',4219)
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
   


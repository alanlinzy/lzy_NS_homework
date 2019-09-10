
import socket
import time  
import ERM
import asyncio

class server(asyncio.Protocol):
    def connection_made(self,transport):
        peername = transport.get_extra_info("peername")
        print(peername)
        self.transport = transport

    
            
    def write_func(self,message):
        #socket.send()

        self.transport.write(message.encode())
        print(message)
    
    def data_received(self,message):
        print(message.decode())
        game = ERM.EscapeRoomGame(output = self.write_func )
        game.create_game(cheat=True)
        game.start()
        #print(s.recv(1024))
        while game.status == "playing":
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
                    output = game.command(command)
                
                
        
        
if __name__=="__main__":
    loop = asyncio.get_event_loop()
    # Each client connection will create a new protocol instance
    c = loop.create_server(server, '127.0.0.1', 54216)
    server = loop.run_until_complete(c)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
   


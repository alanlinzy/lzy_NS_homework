from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import STRING,BOOL# whatever field types you need

class GameCommandPacket(PacketType):
    DEFINITION_IDENTIFIER = "gamecommandpacket"# whatever you want
    DEFINITION_VERSION = "0.0"# whatever you want

    FIELDS = [
        
        ("gamecommand",STRING)# whatever you want here
    ]

    @classmethod
    def create_game_command_packet(cls, s):
        return cls( gamecommand =s)# whatever arguments needed to construct the packet
    
    def command(self):
        return self.gamecommand# whatever you need to get the command for the game
    
class GameResponsePacket(PacketType):
    DEFINITION_IDENTIFIER = "gameresponsepacket"# whatever you want
    DEFINITION_VERSION = "0.0"# whatever you want

    FIELDS = [
        ("isgameover",BOOL)
        ("gamestatus",STRING),
        ("gameresponse",STRING)# whatever you want here
    ]

    @classmethod
    def create_game_response_packet(cls, response, status):
        return cls(gameresponse = response,gamestatus =status, isgameover = True if self.status == "escaped" or status =="dead" else False) # whatever you need to construct the packet )
    
    def game_over(self):

        return self.isgameover# whatever you need to do to determine if the game is over
    
    def status(self):
        return self.gamestatus# whatever you need to do to return the status
    
    def response(self):
        return self.gameresponse# whatever you need to do to return the response

from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT8, STRING, BUFFER
from playground.network.packet.fieldtypes.attributes import Optional

class GameCommandPacket(PacketType):
    DEFINITION_IDENTIFIER = "commandpacket"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("command", STRING)
    ]

    @classmethod
    def create_game_command_packet(cls, s):
        return cls(command=s)
    
    def command(self):
        return self.command
    
class GameResponsePacket(PacketType):
    DEFINITION_IDENTIFIER = "responsepacket"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
         ("response", STRING),
         ("status", STRING)
    ]

    @classmethod
    def create_game_response_packet(cls, response, status):
        return cls(response=response, status=status)

    def game_over(self):
        # MUST RETURN A BOOL
        return self.status in ("dead", "escaped")
    
    def status(self):
        # MUST RETURN game.status (as a string)
        return self.status
    
    def response(self):
        # MUST return game response as a string
        return self.response


class GameInitPacket(PacketType):
    DEFINITION_IDENTIFIER = "initpacket"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
         ("username", STRING)
    ]

class GameRequirePayPacket(PacketType):
    DEFINITION_IDENTIFIER = "requirepaypacket"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("unique_id", STRING),
        ("account", STRING),
        ("amount", UINT8)
    ]

class GamePayPacket(PacketType):
    DEFINITION_IDENTIFIER = "paypacket"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("receipt", BUFFER),
        ("receipt_signature", BUFFER)
    ]

def create_game_init_packet(username):
    return GameInitPacket(username=username)

def process_game_init(pkt):
    return pkt.username

def create_game_require_pay_packet(unique_id, account, amount):
    return GameRequirePayPacket(unique_id=unique_id, account=account, amount=amount)

def process_game_require_pay_packet(pkt):
    return (pkt.unique_id, pkt.account, pkt.amount)

def create_game_pay_packet(receipt, receipt_signature):
    return GamePayPacket(receipt=receipt, receipt_signature=receipt_signature)

def process_game_pay_packet(pkt):
    return (pkt.receipt, receipt_signature)

def create_game_response(response, status):
    return GameResponsePacket(response=response, status=status)

def process_game_response(pkt):
    return pkt.response, pkt.status

def create_game_command(command):
    return GameCommandPacket(command=command)

def process_game_command(pkt):
    return pkt.command

from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BUFFER
from playground.network.packet.fieldtypes.attributes import Optional

class GameCommandPacket(PacketType):
    DEFINITION_IDENTIFIER = "exercise7.gamecommand"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("command_string", STRING)
    ]

    @classmethod
    def create_game_command_packet(cls, s):
        return cls(command_string=s)
    
    def command(self):
        return self.command_string
    
class GameResponsePacket(PacketType):
    DEFINITION_IDENTIFIER = "exercise7.gameresponse"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("response_string", STRING),#({Optional: True})
        ("status_string", STRING)
    ]

    @classmethod
    def create_game_response_packet(cls, response, status):
        return cls(response_string=response, status_string=status)

    def game_over(self):
        # MUST RETURN A BOOL
        return self.status_string in ("dead", "escaped")
    
    def status(self):
        # MUST RETURN game.status (as a string)
        return self.status_string
    
    def response(self):
        # MUST return game response as a string
        return self.response_string


class GameInitRequest(PacketType):
    DEFINITION_IDENTIFIER = "exercise7.gameinit"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("username_string", STRING)
    ]

class GamePaymentRequest(PacketType):
    DEFINITION_IDENTIFIER = "exercise7.gamepaymentrequest"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("unique_id", STRING),
        ("account", STRING),
        ("amount", UINT32)
    ]

class GamePaymentResponse(PacketType):
    DEFINITION_IDENTIFIER = "exercise7.gamepaymentresponse"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("receipt", BUFFER),
        ("receipt_sig", BUFFER)
    ]

def create_game_init_packet(username):
    return GameInitRequest(username_string=username)

def process_game_init(pkt):
    return pkt.username_string

def create_game_require_pay_packet(unique_id, account, amount):
    return GamePaymentRequest(unique_id=unique_id, account=account, amount=amount)

def process_game_require_pay_packet(pkt):
    return (pkt.unique_id, pkt.account, pkt.amount)

def create_game_pay_packet(receipt, receipt_signature):
    return GamePaymentResponse(receipt=receipt, receipt_sig=receipt_signature)

def process_game_pay_packet(pkt):
    return (pkt.receipt, pkt.receipt_sig)

def create_game_response(response, status):
    return GameResponsePacket(string_response=response, status_string=status)

def process_game_response(pkt):
    return pkt.response_string

def create_game_command(command):
    return GameCommandPacket(command_string=command)

def process_game_command(pkt):
    return pkt.command_string

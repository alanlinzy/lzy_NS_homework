# import sys
# import os
# sys.path.insert(0, os.path.abspath('..'))
from playground.network.common import StackingProtocolFactory, StackingProtocol, StackingTransport
import logging
import time
import asyncio
from random import randrange
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT8, UINT32, STRING, BUFFER
from playground.network.packet.fieldtypes.attributes import Optional
from .Crypto_manager import *
# from poop.protocol import POOP
from ..poop.protocol import POOP
import random

logger = logging.getLogger("playground.__connector__." + __name__)


def print_pkt(pkt):  # try to print packet content
    print("-----------")
    for f in pkt.FIELDS:
        f_name = f[0]
        print(str(f_name) + ": " + str(pkt._fields[f_name]._data))
    print("-----------")
    return
class CrapPacketType(PacketType):
    DEFINITION_IDENTIFIER = "crap"
    DEFINITION_VERSION = "1.0"


class HandshakePacket(CrapPacketType):
    DEFINITION_IDENTIFIER = "crap.handshakepacket"
    DEFINITION_VERSION = "1.0"
    NOT_STARTED = 0
    SUCCESS = 1
    ERROR = 2
    FIELDS = [
        ("status", UINT8),
        ("nonce", UINT32({Optional: True})),
        ("nonceSignature", BUFFER({Optional: True})),
        ("signature", BUFFER({Optional: True})),
        ("pk", BUFFER({Optional: True})),
        ("cert", BUFFER({Optional: True}))
    ]


class DataPacket(CrapPacketType):
    DEFINITION_IDENTIFIER = "crap.datapacket"
    DEFINITION_VERSION = "1.0"
    FIELDS = [
        ("data", BUFFER),
        ("signature", BUFFER),
    ]


class CRAPTransport(StackingTransport):
    def connect_protocol(self, protocol):
        self.protocol = protocol

    def write(self, data):
        self.protocol.send_data(data)

    def close(self):
        self.protocol.init_close()


class ErrorHandleClass():
    def handleException(self, e):
        print(e)
def printx(string):
    print(string.center(80, '-')+'\n')


def printError(string):
    print(string.center(80, '!')+'\n')


class CRAP(StackingProtocol):
        def __init__(self, mode):
        super().__init__()
        msg = "{} CRAP init".format(mode)
        printx(msg)

        self._mode = mode
        self.status = 0
        self.higher_transport = None
        self.deserializer = CrapPacketType.Deserializer(
            errHandler=ErrorHandleClass())
        self.shared_secret = None

        self.man = Crypto_manager()

        # generate EC key
        # self.nonce = os.urandom(32)
        # todo: fix this
        self.nonce = random.randrange(10000)
        self.key = self.man.generate_EC_key()
        # get CA's pubk
        with open("keyfile/CA_pubk.pem", "rb") as file:
            self.CA_pubk = self.man.unpemfy_public_key(file.read())
        # get key for cert
        # get cert and generate signature
        pubK_pem = self.man.pemfy_public_key(self.key.public_key())
        if self._mode == "client":
            with open("keyfile/A_key.pem", "rb") as file:
                self.sign_key = self.man.unpemfy_private_key(file.read())
            with open("keyfile/A_cert.pem", "rb") as file:
                self.cert_pem = file.read()
                self.cert = self.man.unpemfy_cert(self.cert_pem)
                self.sig = self.man.generate_RSA_signature(
                    self.sign_key, pubK_pem)

        else:
            with open("keyfile/B_key.pem", "rb") as file:
                self.sign_key = self.man.unpemfy_private_key(file.read())
            with open("keyfile/B_cert.pem", "rb") as file:
                self.cert_pem = file.read()
                self.cert = self.man.unpemfy_cert(self.cert_pem)
                self.sig = self.man.generate_RSA_signature(
                    self.sign_key, pubK_pem)

    def connection_made(self, transport):
        info = "{} CRAP: connection made".format(self._mode)
        print(info)
        logger.debug(info)

        self.transport = transport
        self.higher_transport = CRAPTransport(transport)
        self.higher_transport.connect_protocol(self)

        if self._mode == "client":  # client send first packet
            public_key_pem = self.man.pemfy_public_key(self.key.public_key())
            pkt = HandshakePacket(
                status=0, pk=public_key_pem, signature=self.sig, cert=self.cert_pem, nonce=self.nonce)
            self.send_pkt(pkt)
            print("CRAP: client sent first pkt")

    def send_error_handshake_pkt(self):
        pkt = HandshakePacket(status=2)
        self.send_pkt(pkt)

    def send_pkt(self, pkt):
        self.transport.write(pkt.__serialize__())

    def data_received(self, buffer):
        print("{} CRAP: recv a buffer".format(self._mode))
        self.deserializer.update(buffer)
        for pkt in self.deserializer.nextPackets():
            pkt_type = pkt.DEFINITION_IDENTIFIER
            if pkt_type == HandshakePacket().DEFINITION_IDENTIFIER:
                # check unexpected pkt
                if pkt.status == 2:
                    self.send_error_handshake_pkt()
                    print("BUG CRAP: recv a error handshake pkt")
                    return
                elif self.status == "SUCCESS":
                    self.send_error_handshake_pkt()
                    print("BUG CRAP: recv a handshake pkt when status is SUCCESS")
                    return

                # two cases
                if self._mode == "client":
                    try:
                        # verify cert and sig get EC_pubk
                        self.verify_pkt_cert_and_sig(pkt)
                        # verify nonce
                        self.verify_pkt_nonce(pkt)
                    except Exception as e:
                        print("{} CRAP HANDSHAKE ERROR: exception when verifying cert, sig, or nonce, it says: {}".format(
                            self._mode, e))
                        self.send_error_handshake_pkt()
                        return
                    # generate shared secret
                    self.shared_secret = self.man.get_EC_derived_key(
                        self.key, self.peer_EC_pubk)
                    print("CRAP {}: shared key generated".format(self._mode))
                    # send response pkt
                    nonce_sig = self.man.generate_RSA_signature(
                        self.sign_key, pkt.nonce)
                    self.send_pkt(HandshakePacket(
                        status=1, nonceSignature=nonce_sig))
                    continue
                else:
                    # tow cases
                    if pkt.status == 0:
                        # verify cert and sig, get EC_pubk
                        try:
                            self.verify_pkt_cert_and_sig(pkt)
                        except Exception as e:
                            print("{} CRAP HANDSHAKE ERROR: exception when verifying cert or sig it says: \"{}\"".format(
                                self._mode, e))
                            self.send_error_handshake_pkt()
                            return
                        # send hello, challenge, responce pkt
                        nonce_sig = self.man.generate_RSA_signature(
                            self.sign_key, pkt.nonce)
                        public_EC_key_pem = self.man.pemfy_public_key(
                            self.key.public_key())
                        self.send_pkt(HandshakePacket(status=1, nonceSignature=nonce_sig,
                                                      pk=public_EC_key_pem, signature=self.sig, cert=self.cert_pem, nonce=self.nonce))
                        continue

                    else:
                        # verify nonce
                        try:
                            self.verify_pkt_nonce(pkt)
                        except Exception as e:
                            print("{} CRAP HANDSHAKE ERROR: exception when verifying once it says: \"{}\"".format(
                                self._mode, e))
                            self.send_error_handshake_pkt()
                            return
                        # generate shared secret
                        self.shared_secret = self.man.get_EC_derived_key(
                            self.key, self.peer_EC_pubk)
                        print("CRAP {}: shared key generated".format(self._mode))
                        continue

    def verify_pkt_cert_and_sig(self, pkt):
        pkt_cert = self.man.unpemfy_cert(pkt.cert)
        cert_pubk = self.man.get_public_key_from_cert(pkt_cert)
        pkt_EC_pubk = self.man.unpemfy_public_key(pkt.pk)

        # verify cert, then trust cert_pubk
        self.man.verify_cert(self.CA_pubk, pkt_cert)
        print("{} CRAP: passed cert verify".format(self._mode))

        # verify sig, then trust pkt_EC_pubk(pkt.pk)
        # TODO: define date
        self.man.verify_RSA_signature(cert_pubk, pkt.signature, pkt.pk)

        print("{} CRAP: passed sig verify".format(self._mode))
        self.peer_cert_pubk = cert_pubk
        self.peer_EC_pubk = pkt_EC_pubk

    def verify_pkt_nonce(self, pkt):
        # TODO: change back!
        self.man.verify_RSA_signature(
            self.peer_cert_pubk, pkt.nonceSignature, self.nonce)

    def connection_lost(self, exc):
        logger.debug(
            "{} CRAP connection lost. Shutting down higher layer.".
            format(self._mode))
        self.higherProtocol().connection_lost(exc)

        
CRAPClientFactory = StackingProtocolFactory.CreateFactoryType(
    lambda: POOP(mode="client"), lambda: CRAP(mode="client"))

CRAPServerFactory = StackingProtocolFactory.CreateFactoryType(
    lambda: POOP(mode="server"), lambda: CRAP(mode="server"))


                    

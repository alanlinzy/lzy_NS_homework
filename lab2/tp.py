from playground.network.common import StackingProtocolFactory, StackingProtocol, StackingTransport
from ..poop.protocol import POOP

import logging
import time
import asyncio
import datetime
import os
from random import randrange
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT8, UINT32, STRING, BUFFER
from playground.network.packet.fieldtypes.attributes import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import PublicFormat, Encoding, load_pem_public_key
from cryptography import x509
from cryptography.x509.oid import NameOID
class CrapPacketType(PacketType):
    DEFINITION_IDENTIFIER = "crap"
    DEFINITION_VERSION = "1.0"

class HandshakePacket(CrapPacketType):
    DEFINITION_IDENTIFIER = "crap.handshakepacket"
    DEFINITION_VERSION = "1.0"

    NOT_STARTED = 0
    SUCCESS     = 1
    ERROR       = 2

    FIELDS = [
        ("status", UINT8),
        ("nonce", UINT32({Optional:True})),
            ("nonceSignature", BUFFER({Optional:True})),
        ("signature", BUFFER({Optional:True})),
        ("pk", BUFFER({Optional:True})),
        ("cert", BUFFER({Optional:True}))
    ]
class DataPacket(CrapPacketType):
    DEFINITION_IDENTIFIER = "crap.datapacket"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("data", BUFFER),
        ("signature", BUFFER)
    ]


class CRAPTransport(StackingTransport):
    def connect_protocol(self, protocol):
        self.protocol = protocol
    def write(self, data):
        self.protocol.send_data(data)
    def close(self):
        self.protocol.close()


class CRAP(StackingProtocol):
    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        self.higher_transport = None
        self.deserializer = CrapPacketType.Deserializer()
        self.handshook = False

    def connection_made(self, transport):
        print("CRAP CONNECTED")
        try:
            self.transport = transport
            if self.mode == "client":
                self.send_first_handshake_pkt(None)
        except Exception as e:
            print("ERROR OCCURED")
            print(e)

    def data_received(self, buffer):
        print("DATA RECEIVED")
        try:
            self.deserializer.update(buffer)
            for pkt in self.deserializer.nextPackets():
                if pkt.DEFINITION_IDENTIFIER == "crap.handshakepacket":
                    print("RECEIVED: " + str(pkt.status))
                    if pkt.status == 0:
                        if self.mode == "server":
                            self.verify_pk_signature(pkt)
                            self.send_first_handshake_pkt(pkt)
                        continue
                    if pkt.status == 1:
                        if self.mode == "client":
                            self.verify_pk_signature(pkt)
                            self.verify_nonce_signature(pkt)
                            nonce_signature = self.signing_key.sign(bytes(pkt.nonce), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
                            succ_pkt = HandshakePacket(status=1, nonceSignature=nonce_signature)
                            print("SENDING CLIENT 2")
                            self.transport.write(succ_pkt.__serialize__())
                        else:
                            self.verify_nonce_signature(pkt)
                        self.derive_keys()
                        self.handshook = True
                        #self.higher_transport = CRAPTransport(self.transport)
                        #self.higher_transport.connect_protocol(self)
                        #self.higherProtocol().connection_made(self.higher_transport)
                        continue
                    if pkt.status == 2:
                        self.transport.close()
                        continue
        except Exception as e:
            print("ERROR OCCURED")
            print(e)

    def send_first_handshake_pkt(self, pkt):
        #print("Generating private key")
        self.private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
        #print("Generating public key")
        self.public_key = self.private_key.public_key()
        #print("Generating signing key")
        self.signing_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        verification_key = self.signing_key.public_key()

        #print("Generating garbage key")
        garbage_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

        #print("Generating certificate")
        certificate = x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u'garbage'),])).issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u'more garbage'),])).serial_number(x509.random_serial_number()).not_valid_before(datetime.datetime.utcnow()).not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=10)).public_key(verification_key).sign(garbage_key, hashes.SHA256(), default_backend())

        #print("Signing public key")
        public_key_bytes = self.public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        signature = self.signing_key.sign(public_key_bytes, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())

        #print("Generating nonce")
        self.nonce = randrange(1000000)

        status = 0 if self.mode == "client" else 1

        if pkt:
            #print("Signing nonce")
            nonce_signature = self.signing_key.sign(bytes(pkt.nonce), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
            #print("Generating packet")
            pkt = HandshakePacket(status=status, pk=public_key_bytes, signature=signature, cert=certificate.public_bytes(Encoding.PEM), nonce=self.nonce, nonceSignature=nonce_signature)
            print("SENDING SERVER 1")
        else:
            #print("Generating packet")
            pkt = HandshakePacket(status=status, pk=public_key_bytes, signature=signature, cert=certificate.public_bytes(Encoding.PEM), nonce=self.nonce)
            print("SENDING CLIENT 1")

        self.transport.write(pkt.__serialize__())


    def verify_pk_signature(self, pkt):
        self.verification_key = x509.load_pem_x509_certificate(pkt.cert, default_backend()).public_key()
        try:
            self.verification_key.verify(pkt.signature, pkt.pk, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
            self.peer_public_key = load_pem_public_key(pkt.pk, default_backend())
            print("Pass PK verify")
        except:
            print("PK VERIFY ERROR! CLOSING CONNECTION")
            pkt = HandshakePacket(status=2)
            #self.higherProtocol().connection_lost(None)
            self.transport.write(pkt.__serialize__())
            self.transport.close()

    def verify_nonce_signature(self, pkt):
        try:
            verification_key.verify(pkt.nonceSignature, bytes(self.nonce), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
            print("Pass Nonce verify")
        except:
            print("NONCE VERIFY ERROR! CLOSING CONNECTION")
            pkt = HandshakePacket(status=2)
            #self.higherProtocol().connection_lost(None)
            self.transport.write(pkt.__serialize__())
            self.transport.close()

    def derive_keys(self):
        pass

CRAPClientFactory = StackingProtocolFactory.CreateFactoryType(
    lambda: POOP(mode="client"), lambda: CRAP(mode="client"))

CRAPServerFactory = StackingProtocolFactory.CreateFactoryType(
    lambda: POOP(mode="server"), lambda: CRAP(mode="server"))

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives.serialization import Encoding
from OpenSSL import crypto, SSL
def connection_made():#(self, transport):
    #self.transport = transport
    if self.mode == "CLIENT" or True:
        private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
        public_key = private_key.public_key()
        signing_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        verification_key = signing_key.public_key()
        certificate = crypto.X509()
        certificate.set_pubkey(verification_key)
        signature = signing_key.sign(public_key, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())
        #pkt = HandshakePacket(status=0, pk=public_key, signature=signature, cert=certificate)
        #self.transport.write(pkt.__serialize__())
        crypto.dump_certificate(crypto.FILETYPE_PEM, certificate)
        #crypto.dump_privatekey(crypto.<wbr>FILETYPE_PEM, k)
        #self.private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
        #self.public_key = self.private_key.public_key()
        #self.public_key_bytes = self.public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        #self.signing_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        #self.verification_key = signing_key.public_key()
        #self.certificate = crypto.X509()
        #self.certificate.set_pubkey(verification_key)

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
               ("signature", BUFFER({Optional:True})),
               ("pk", BUFFER({Optional:True})),
               ("cert", BUFFER({Optional:True}))
           ]
class DataPacket(CrapPacketType):
           DEFINITION_IDENTIFIER = "crap.datapacket"
           DEFINITION_VERSION = "1.0"
           FIELDS = [
               ("data", BUFFER),
               ("signature", BUFFER),
           ]

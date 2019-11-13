from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography import x509 
import datetime


# pakcet part
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






# tls handshake part

def connection_made():#(self, transport):
    #self.transport = transport
    if self.mode == "CLIENT" or True:
        private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
        public_key = private_key.public_key()
        signing_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        verification_key = signing_key.public_key()
        #certificate = x509.load_pem_x509_certificate(verification_key, default_backend())
        #certificate.public_bytes(serialization.Encoding.PEM)
        x509subject = generate_subject("whatever")
        certificate = generate_cert("subjectname","issuename",public_key,signing_key)
        signature = signing_key.sign(public_key, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())
        #need to seriallize packet
        pkt = HandshakePacket(status=0, pk=public_key, signature=signature, cert=certificate)
        self.transport.write(pkt.__serialize__())
        
        #crypto.dump_privatekey(crypto.<wbr>FILETYPE_PEM, k)
        #self.private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
        #self.public_key = self.private_key.public_key()
        #self.public_key_bytes = self.public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        #self.signing_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        #self.verification_key = signing_key.public_key()
        #self.certificate = crypto.X509()
        #self.certificate.set_pubkey(verification_key)
        # clientside 
        shared_key = private_key.exchange(ec.ECDH(), pkt.pk)
        derived_key = get_derived_key(shared_key)
    elif self.mode == "SERVER":
        # handshake packet
        if pkt.DEFINITION_IDENTIFIER == "crap.handshakepacket":
            if pkt.status == 2:
                print("ERROR PACKET")
            else:
                if not pkt.pk:
                    print("no pk")
                if not pkt.signture:
                    print("no sig")
                if not pkt.cert:
                    print("no cert")
                if pkt.cert and pkt.pk and pkt.signture:
                    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
                    public_key = private_key.public_key()
                    signing_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
                    verification_key = signing_key.public_key()
                    #verify
                    # verify the signiature  fail: send error else:pass
                    # generate its own ECDH public key
                    shared_key = private_key.exchange(ec.ECDH(), pkt.pk)
                    derived_key = get_derived_key(shared_key)
                    
                    
            
        else:
            print("no handshake packet")
def get_derived_key(shared_key):
    return HKDF(algorithm=hashes.SHA256(),length=32,salt=None,info=b'handshake data',backend=default_backend()).derive(shared_key)
                   
def verify_EC_signature(self, public_key, sig, data):
        chosen_hash = hashes.SHA256()
        public_key.verify(
            sig,
            data,
            ec.ECDSA(chosen_hash)
        )
def generate_subject(self, common_name):
        return x509.Name([
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, u"California"),
            x509.NameAttribute(x509.NameOID.LOCALITY_NAME, u"San Francisco"),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, u"My Company"),
            x509.NameAttribute(x509.NameOID.COMMON_NAME, common_name),
        ])

def generate_cert(self, subject, issuer, public_key, sign_key):
        return x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            public_key
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=10)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
        ).sign(sign_key, hashes.SHA256(), default_backend())











# transfor data part
import os

#from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)

def encrypt(key, plaintext, associated_data):
    # Generate a random 96-bit IV.
    iv = os.urandom(12)

    # Construct an AES-GCM Cipher object with the given key and a
    # randomly generated IV.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    # associated_data will be authenticated but not encrypted,
    # it must also be passed in on decryption.
    encryptor.authenticate_additional_data(associated_data)

    # Encrypt the plaintext and get the associated ciphertext.
    # GCM does not require padding.
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    return (iv, ciphertext, encryptor.tag)

def decrypt(key, associated_data, iv, ciphertext, tag):
    # Construct a Cipher object, with the key, iv, and additionally the
    # GCM tag used for authenticating the message.
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()

    # We put associated_data back in or the tag will fail to verify
    # when we finalize the decryptor.
    decryptor.authenticate_additional_data(associated_data)

    # Decryption gets us the authenticated plaintext.
    # If the tag does not match an InvalidTag exception will be raised.
    return decryptor.update(ciphertext) + decryptor.finalize()

iv, ciphertext, tag = encrypt(
    key,
    b"a secret message!",
    b"authenticated but not encrypted payload"
)

print(decrypt(
    key,
    b"authenticated but not encrypted payload",
    iv,
    ciphertext,
    tag
))





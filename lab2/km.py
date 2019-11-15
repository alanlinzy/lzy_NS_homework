from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding




class Crypto_manager:
    def __init__(self):
        pass
        # self.file_password = b'password'

    # def get_file_password(self):
    #     return self.file_password

    def generate_EC_key(self):
        return ec.generate_private_key(ec.SECP384R1(), default_backend())

    def generate_RSA_key(self):
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )


    def get_EC_derived_key(self, key, peer_public_key, info=b'handshake data'):
        shared_key = key.exchange(ec.ECDH(), peer_public_key)
        return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=info, backend=default_backend()).derive(shared_key)

    def pemfy_private_key(self, key):
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

    def unpemfy_private_key(self, key_pem):
        return serialization.load_pem_private_key(
            key_pem,
            password=None,
            backend=default_backend()
        )

    def generate_subject(self, common_name):
        return x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),])


    def generate_cert(self, subject, issuer, subject_public_key, issuer_sign_key):
        return x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            subject_public_key
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=10)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
        ).sign(issuer_sign_key, hashes.SHA256(), default_backend())

    def pemfy_cert(self, cert):
        return cert.public_bytes(serialization.Encoding.PEM)

    def unpemfy_cert(self, cert_pem):
        return x509.load_pem_x509_certificate(cert_pem, default_backend())

    def pemfy_public_key(self, public_key):
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

    def unpemfy_public_key(self, public_key_pem):
        return load_pem_public_key(public_key_pem, default_backend())

    def get_public_key_from_cert(self, cert):
        public_key = cert.public_key()
        if isinstance(public_key, rsa.RSAPublicKey):
            return public_key
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            return public_key
        else:
            return None





    def verify_cert(self, issuer_public_key, cert_to_verify):
        issuer_public_key.verify(
            cert_to_verify.signature,
            cert_to_verify.tbs_certificate_bytes,
            # Depends on the algorithm used to create the certificate
            padding.PKCS1v15(),
            cert_to_verify.signature_hash_algorithm,
        )

    def generate_EC_signature(self, sign_key, data_to_sign):
        return sign_key.sign(data_to_sign, ec.ECDSA(hashes.SHA256()))

    def verify_EC_signature(self, signer_public_key, sig_to_verify, expected_data):
        chosen_hash = hashes.SHA256()
        signer_public_key.verify(
            sig_to_verify,
            expected_data,
            ec.ECDSA(chosen_hash)
        )
               

    def generate_RSA_signature(self, sign_key, data_to_sign):
        if type(data_to_sign) != bytes:
            data_to_sign = bytes(data_to_sign)
        return sign_key.sign(
            data_to_sign,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def verify_RSA_signature(self, signer_public_key, sig_to_verify, expected_data):
        if type(expected_data) != bytes:
            expected_data = bytes(expected_data)
        signer_public_key.verify(
            sig_to_verify,
            expected_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
              

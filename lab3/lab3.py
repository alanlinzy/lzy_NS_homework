import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import unittest

from cryptography.hazmat.backends import default_backend
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
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

    def hash(self, data_to_hash):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data_to_hash)
        return digest.finalize()

    def generate_AESGCM_key(self):
        return AESGCM.generate_key(bit_length=128)

    def AESGCM_enc(self, key, nonce, data, aad=None):
        return AESGCM(key).encrypt(nonce, data, aad)

    def ASEGCM_dec(self, key, nonce,ct, aad=None):
        return AESGCM(key).decrypt(nonce, ct, aad)

    def generate_CSR(self, key , path,common_name, DNSName, country_name = "US", state_name = "Maryland", locality_name = "Baltimore", organization_name = "JHU"):
        csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country_name),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state_name),
            x509.NameAttribute(NameOID.LOCALITY_NAME, locality_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization_name),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])).add_extension(
            x509.SubjectAlternativeName([
                # Describe what sites we want this certificate for.
                x509.DNSName(DNSName)
            ]),
            critical = False,
        ).sign(key, hashes.SHA256(), default_backend())

        with open(path,"wb") as f:
            f.write(csr.public_bytes(serialization.Encoding.PEM))
    def generate_EC_key(self):
        return ec.generate_private_key(
            ec.SECP384R1(),
            default_backend()
        )

    def generate_RSA_key(self):
        return rsa.generate_private_key(
            public_exponent = 65537,
            key_size        = 2048,
            backend         = default_backend()
        )

    def get_EC_derived_key(self, key, peer_public_key):
        return key.exchange(ec.ECDH(), peer_public_key)

    def pemfy_private_key(self, key):
        return key.private_bytes(
            encoding             = serialization.Encoding.PEM,
            format               = serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm = serialization.NoEncryption()
        )

    def unpemfy_private_key(self, key_pem, password= None):
        return serialization.load_pem_private_key(
            key_pem,
            password = password,
            backend  = default_backend()
        )

    def generate_subject(self, common_name):
        return x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Maryland"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Baltimore"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"JHU"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])

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
            critical = False,
        ).sign(issuer_sign_key, hashes.SHA256(), default_backend())

    def pemfy_cert(self, cert):
        return cert.public_bytes(serialization.Encoding.PEM)
    def unpemfy_cert(self, cert_pem):
        return x509.load_pem_x509_certificate(cert_pem, default_backend())

    def pemfy_public_key(self, public_key):
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def unpemfy_public_key(self, public_key_pem):
        return load_pem_public_key(public_key_pem, default_backend())

    def get_subject_common_name_from_cert(self, cert):
        return cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

    def get_issuer_common_name_from_cert(self, cert):
        return cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

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
        return sign_key.sign(
            data_to_sign,
            ec.ECDSA(hashes.SHA256())
        )

    def verify_EC_signature(self, signer_public_key, sig_to_verify, expected_data):
        chosen_hash = hashes.SHA256()
        signer_public_key.verify(
            sig_to_verify,
            expected_data,
            ec.ECDSA(chosen_hash)
        )

    def generate_RSA_signature(self, sign_key, data_to_sign):
        if type(data_to_sign) != bytes:
            data_to_sign = str(data_to_sign).encode('ASCII')
        return sign_key.sign(
            data_to_sign,
            padding.PSS(
                mgf         = padding.MGF1(hashes.SHA256()),
                salt_length = padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def verify_RSA_signature(self, signer_public_key, sig_to_verify, expected_data):
        if type(expected_data) != bytes:
            expected_data = str(expected_data).encode('ASCII')
        signer_public_key.verify(
            sig_to_verify,
            expected_data,
            padding.PSS(
                mgf         = padding.MGF1(hashes.SHA256()),
                salt_length = padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )


# folder                    = "test_keyfile/"
keyfile_folder            = "keyfiles/"
folder = keyfile_folder
team2_cert_pem_path       = keyfile_folder + "team2_cert.pem"
team2_56_78_key_pem_path  = keyfile_folder + "team2_56_78_key.pem"
team2_56_78_cert_pem_path = keyfile_folder + "team2_56_78_cert.pem"
root_pubk_pem_path        = keyfile_folder + "20194_root_pubk.pem"
root_cert_pem_path        = keyfile_folder + "20194_root_cert.pem"

class Test_croppto_manager(unittest.TestCase):
    def setUp(self):
        self.man            = Crypto_manager()
        self.issuer_key     = self.man.generate_RSA_key()
        self.client_RSA_key = self.man.generate_RSA_key()
        self.server_RSA_key = self.man.generate_RSA_key()
        self.client_subject = self.man.generate_subject("test_client_subject")
        self.issuer_subject = self.man.generate_subject("test_issuer_subject")
        self.client_cert    = self.man.generate_cert(self.client_subject, self.issuer_subject,self.client_RSA_key.public_key(), self.issuer_key)
        self.client_EC_key  = self.man.generate_EC_key()
        self.server_EC_key  = self.man.generate_EC_key()
        self.data           = b"test sig data"

    def test_rule1(self):
        keyfile_folder  = "lab3_keyfiles/rule1/"
        domain = "20194.2.57.98"
        # get cert and generate signature
        with open(keyfile_folder + domain + "_key.pem", "rb") as f:
            domain_key_pem = f.read()
            domain_key = self.man.unpemfy_private_key(domain_key_pem)
        with open(keyfile_folder + domain + "_cert.pem", "rb") as f:
            domain_cert_pem = f.read()
            domain_cert     = self.man.unpemfy_cert(domain_cert_pem)
        with open(keyfile_folder + "team2_cert.pem", "rb") as f:
            team2_cert_pem = f.read()
            team2_cert    = self.man.unpemfy_cert(team2_cert_pem)
        with open(keyfile_folder + "root_cert.pem", "rb") as f:
            root_cert_pem = f.read()
            root_cert     = self.man.unpemfy_cert(root_cert_pem)

        self.assertEqual("20194.", self.man.get_issuer_common_name_from_cert(team2_cert))
        self.assertEqual("20194.2.", self.man.get_subject_common_name_from_cert(team2_cert))
        self.assertEqual("20194.2.", self.man.get_issuer_common_name_from_cert(domain_cert))
        self.assertEqual(domain, self.man.get_subject_common_name_from_cert(domain_cert))

        self.man.verify_cert(self.man.get_public_key_from_cert(root_cert), team2_cert)
        self.man.verify_cert(self.man.get_public_key_from_cert(team2_cert), domain_cert)

    def test_rule2(self):
        keyfile_folder = "lab3_keyfiles/rule2/"
        domain         = "20194.2.57.98"
        with open(keyfile_folder + domain + "_key.pem", "rb") as f:
            domain_key_pem = f.read()
            team2_key     = self.man.unpemfy_private_key(team2_key_pem)

        self.assertEqual("20194.2.", self.man.get_issuer_common_name_from_cert(domain_cert))
        self.assertEqual(domain, self.man.get_subject_common_name_from_cert(domain_cert))

        self.man.verify_cert(team2_key.public_key(), domain_cert)

    def test_rule4(self):
        keyfile_folder  = "lab3_keyfiles/rule4/"
        domain = "20194.2.57.98"
        # cert
        with open(keyfile_folder + domain + "_key.pem", "rb") as f:
            domain_key_pem = f.read()
            domain_key = self.man.unpemfy_private_key(domain_key_pem)
        with open(keyfile_folder + domain + "_cert.pem", "rb") as f:
            domain_cert_pem = f.read()
            domain_cert     = self.man.unpemfy_cert(domain_cert_pem)
            # NOTE: here is team4
        with open(keyfile_folder + "team4_cert.pem", "rb") as f:
            team4_cert_pem = f.read()
            team4_cert    = self.man.unpemfy_cert(team4_cert_pem)
        with open("keyfiles/root_cert.pem", "rb") as f:
            root_cert_pem = f.read()
            root_cert     = self.man.unpemfy_cert(root_cert_pem)

        self.assertEqual("20194.", self.man.get_issuer_common_name_from_cert(team4_cert))
        self.assertEqual("20194.4.", self.man.get_subject_common_name_from_cert(team4_cert))
        self.assertEqual("20194.4.", self.man.get_issuer_common_name_from_cert(domain_cert))
        self.assertEqual(domain, self.man.get_subject_common_name_from_cert(domain_cert))

        self.man.verify_cert(self.man.get_public_key_from_cert(root_cert), team4_cert)
        self.man.verify_cert(self.man.get_public_key_from_cert(team4_cert), domain_cert)

    def test_cert_chain(self):
        domain = "20194.2.56.98"
        # get cert and generate signature
        with open(keyfile_folder + domain + "_key.pem", "rb") as f:
            domain_key_pem = f.read()
            domain_key = self.man.unpemfy_private_key(domain_key_pem)
        with open(keyfile_folder + domain + "_cert.pem", "rb") as f:
            domain_cert_pem = f.read()
            domain_cert     = self.man.unpemfy_cert(domain_cert_pem)
        with open("keyfiles/team2_cert.pem", "rb") as f:
            team2_cert_pem = f.read()
            team2_cert    = self.man.unpemfy_cert(team2_cert_pem)
        with open("keyfiles/20194_root_cert.pem", "rb") as f:
            root_cert_pem = f.read()
            root_cert    = self.man.unpemfy_cert(root_cert_pem)

        self.assertEqual("20194.", self.man.get_issuer_common_name_from_cert(team2_cert))
        self.assertEqual("20194.2.", self.man.get_subject_common_name_from_cert(team2_cert))
        self.assertEqual("20194.2.", self.man.get_issuer_common_name_from_cert(domain_cert))
        self.assertEqual(domain, self.man.get_subject_common_name_from_cert(domain_cert))

        self.man.verify_cert(self.man.get_public_key_from_cert(root_cert), team2_cert)
        self.man.verify_cert(self.man.get_public_key_from_cert(team2_cert), domain_cert)

    def test_team2_1_1_cert(self):
        with open("keyfiles/team2_1_1_cert.pem", "rb") as f:
            team2_1_1_cert = self.man.unpemfy_cert(f.read())
        with open("keyfiles/team2_pubk.pem", "rb") as f:
            team2_pubk = self.man.unpemfy_public_key(f.read())
        self.man.verify_cert(team2_pubk,team2_1_1_cert)

    def test_class_cert(self):
        with open("keyfiles/20194_root_cert.pem","rb") as f:
            root_pubk = self.man.get_public_key_from_cert(self.man.unpemfy_cert(f.read()))
        with open("keyfiles/team2_cert.pem", "rb") as f:
            team2_cert = self.man.unpemfy_cert(f.read())
        self.man.verify_cert(root_pubk, team2_cert)

        self.assertEqual("20194.", self.man.get_issuer_common_name_from_cert(team2_cert))
        self.assertEqual("20194.4.", self.man.get_subject_common_name_from_cert(team2_cert))
        self.man.verify_cert(root_pubk, team2_cert)

    def test_hash(self):
        hash1 = self.man.hash(self.data * 10)
        test = hash1[:11]
        print(self.man.hash(self.data))

    def test_AESGCM(self):
        # aad   = b"authenticated but unencrypted data"
        key   = self.man.generate_AESGCM_key()
        nonce = os.urandom(12)
        ct    = self.man.AESGCM_enc(key, nonce, self.data)
        pt    = self.man.ASEGCM_dec(key, nonce, ct)
        self.assertEqual(pt, self.data)

    def test_key_pemfy(self):
        key_pem       = self.man.pemfy_private_key(self.client_RSA_key)
        key_pem_again = self.man.pemfy_private_key(self.man.unpemfy_private_key(key_pem))
        self.assertEqual(key_pem, key_pem_again)

        pub_key_pem       = self.man.pemfy_public_key(self.client_RSA_key.public_key())
        pub_key_pem_again = self.man.pemfy_public_key(self.man.unpemfy_public_key(pub_key_pem))
        self.assertEqual(pub_key_pem, pub_key_pem_again)

        key_pem       = self.man.pemfy_private_key(self.client_EC_key)
        key_pem_again = self.man.pemfy_private_key(self.man.unpemfy_private_key(key_pem))
        self.assertEqual(key_pem, key_pem_again)
        pub_key_pem       = self.man.pemfy_public_key(self.client_EC_key.public_key())
        pub_key_pem_again = self.man.pemfy_public_key(self.man.unpemfy_public_key(pub_key_pem))
        self.assertEqual(pub_key_pem, pub_key_pem_again)

    def test_cert(self):
        # test pemfy
        cert_pem            = self.man.pemfy_cert(self.client_cert)
        cert_pem_again = self.man.pemfy_cert(self.man.unpemfy_cert(cert_pem))
        self.assertEqual(cert_pem, cert_pem_again)
        # test verify
        try:
            self.man.verify_cert(self.issuer_key.public_key(), self.client_cert)
        except Exception as e:
            self.fail("fail verify cert")

        self.assertRaises(
            Exception,
            self.man.verify_cert,
            self.server_RSA_key.public_key(),
            self.client_cert
        )

    def test_cert_get_pubk_and_common_name(self):
        derived_pubk = self.man.get_public_key_from_cert(self.client_cert)
        # generate sig
        sig = self.man.generate_RSA_signature(self.client_RSA_key, self.data)
        try:
            self.man.verify_RSA_signature(
                self.client_RSA_key.public_key(), sig, self.data)
        except:
            self.fail("orignal pubk is wrong")

        try:
            self.man.verify_RSA_signature(derived_pubk, sig, self.data)
        except:
            self.fail("pubk from cert is wrong")

    def test_cert_get_common_name(self):
        with open("keyfiles/team2_56_78_cert.pem" , "rb") as f:
            cert         = self.man.unpemfy_cert(f.read())
            subject_name = self.man.get_subject_common_name_from_cert(cert)
            issuer_name  = self.man.get_issuer_common_name_from_cert(cert)
            print(subject_name)
            print(issuer_name)
        with open("keyfiles/team2_cert.pem" , "rb") as f:
            cert         = self.man.unpemfy_cert(f.read())
            subject_name = self.man.get_subject_common_name_from_cert(cert)
            issuer_name  = self.man.get_issuer_common_name_from_cert(cert)
            print(subject_name)
            print(issuer_name)

    def test_EC_derive_key(self):
        server_derived_key = self.man.get_EC_derived_key(
            self.server_EC_key,
            self.client_EC_key.public_key())
        client_derived_key = self.man.get_EC_derived_key(
            self.client_EC_key,
            self.server_EC_key.public_key())
        self.assertEqual(server_derived_key, client_derived_key)

    def test_EC_signature(self):
        sig = self.man.generate_EC_signature(self.client_EC_key, self.data)
        try:
            self.man.verify_EC_signature(self.client_EC_key.public_key(), sig, self.data)
        except:
            self.fail("fail verify EC signature")

        self.assertRaises(
            Exception,
            self.man.verify_EC_signature,
            self.client_EC_key.public_key(),
            sig,
            self.data+b'1'
        )

    def test_RSA_signature(self):
        sig = self.man.generate_RSA_signature(self.client_RSA_key, self.data)
        try:
            self.man.verify_RSA_signature(
                self.client_RSA_key.public_key(),
                sig,
                self.data)
        except:
            self.fail("exception when verify true sig")
        self.assertRaises(
            Exception,
            self.man.verify_EC_signature,
            self.client_EC_key.public_key(),
            sig,
            self.data+b"a")

    def test_RSA_signatrue_int(self):
        sig=self.man.generate_RSA_signature(self.client_RSA_key, 1888)
        try:
            self.man.verify_RSA_signature(
                self.client_RSA_key.public_key(),
                sig,
                1888
            )
        except:
            self.fail("RSA sig fail verify")

        self.assertRaises(
            Exception,
            self.man.verify_RSA_signature,
            self.client_RSA_key.public_key(),
            1888+1
        )

if __name__ =="__main__":
    unittest.main()

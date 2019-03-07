import hashlib
import ecdsa

class Wallet: 
    def __init__(self, node, new = False):
        if not new:
            try: 
                priv_key, pub_key = self.loadCredentials()
            except:
                priv_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
                pub_key = priv_key.get_verifying_key()
        else: 
            priv_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
            pub_key = priv_key.get_verifying_key()
        self.priv_key = priv_key
        self.pub_key = pub_key
        self.node = node
        self.node.set_pub_key(self.pub_key)

    def get_pub_key(self):
        return self.pub_key.to_string.hex()

    def loadCredentials(self):
        keys = open("keystore", "rb").read()
        priv_key = ecdsa.SigningKey.from_pem(keys)
        pub_key = priv_key.get_verifying_key()
        return priv_key, pub_key

    def generateTransaction(self, amount, recipient):
        return f"{amount:#0{15}x}" + self.pub_key.to_string().hex() + recipient.to_string().hex()

    def signTransaction(self, transaction_hex):
        return self.priv_key.sign(transaction_hex.encode('utf-8'))

    def send(self, amount, recipient):
        """ send amount Sats to recipient"""
        transaction = self.generateTransaction(amount, recipient)
        sig = self.signTransaction(transaction)
        self.node.pushTransaction(transaction, sig)

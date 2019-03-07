import hashlib


class Block: 
    def __init__(self, height, data, prevHash = None):
        self.height = height
        self.nonce = None
        self.data = data
        self.prevHash = prevHash
        self.hash = None
        self.transactions = { "Regular": [] }
        self.blockreward = 25

    def __str__(self):
        return "Block " + str(self.height) + " - " + str(self.data)

    def __repr__(self):
        return "Block " + str(self.height)

    def tryNonce(self, nonce):
        self.nonce = nonce
        contents = str(self.height) + str(self.nonce) + str(self.data) + str(self.prevHash) + str(self.transactions)
        self.hash = hashlib.sha256(contents.encode("utf-8")).hexdigest()
        return self.hash

    def getReward(self, pub_key):
        self.transactions["Coinbase"] = f"{self.blockreward:#0{15}x}" + pub_key.to_string().hex()

    def addTransaction(self, hexTr, sig):
        self.transactions["Regular"].append((hexTr, sig))
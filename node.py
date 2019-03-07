import hashlib
import random
import datetime
import ecdsa
from block import Block

class Node: 
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.transaction_pool = []
        self.accounts = {}
        self.pub_key = None
        self.peers = []
        self.name = "Anon"
        self.lastBlockProcessed = None

    def mineBlock(self, block, listenForNewBlocks = True):
        # Returns bool success
        count = 0
        hash = block.tryNonce(random.randint(1, 20000000000))
        while hash[:self.blockchain.difficulty] != '0' * self.blockchain.difficulty:
            if listenForNewBlocks and count % 1e5 == 0:
                outOfDate = self.syncChain()
                if outOfDate:
                    return False
            hash = block.tryNonce(random.randint(1, 20000000000))
            count += 1
        block.hash = hash
        outOfDate = self.syncChain()
        if outOfDate:
            return False
        self.blockchain.blocks.append(block)
        self.lastBlockProcessed = block
        print(self.name + " mined block with hash " + block.hash)
        return True

    def mineOneBlock(self, pub_key=None):
        pub_key = self.pub_key or pub_key
        if pub_key is None:
            raise ValueError("No public key provided!")
        if len(self.blockchain.blocks) == 0:
            genesis = Block(0, "Chancellor on brink of second bailout for banks")
            genesis.getReward(pub_key)
            self.mineBlock(genesis)
            self.settleTransactions(genesis)
            return 
        lastBlock = self.blockchain.blocks[-1]
        newBlock = Block(lastBlock.height + 1, "Mined at " + str(datetime.datetime.now()), lastBlock.hash)
        newBlock.getReward(pub_key)
        for transaction in self.transaction_pool:
            newBlock.addTransaction(transaction[0], transaction[1])
        while not self.mineBlock(newBlock, True):
            continue
        self.settleTransactions(newBlock)

    def mine(self, pub_key = None):
        pub_key = self.pub_key or pub_key
        if pub_key is None:
            raise ValueError("No public key provided!")
        while True:
            self.mineOneBlock()

    def readCoinbase(self, hexStr):
        amount = int(hexStr[:15], 16)
        recipient = hexStr[15:]
        return recipient, amount

    def settleTransactions(self, newValidBlock):
        # Handle Coinbase
        miner, blockReward = self.readCoinbase(newValidBlock.transactions["Coinbase"])
        self.accounts[miner] = self.accounts.get(miner, 0 ) + min(blockReward, self.blockchain.blockReward)
        # Handle Regular tranactions
        for (transaction, _ )in newValidBlock.transactions["Regular"]:
            sender_key, receiver_key, amount = self.readHexTransaction(transaction)
            sender = sender_key.to_string().hex()
            receiver = receiver_key.to_string().hex()
            self.accounts[sender] -= amount
            self.accounts[receiver] = self.accounts.get(receiver, 0) + amount

    def transactionIsValid(self, transaction, sig):
        sender, _, amount = self.readHexTransaction(transaction)
        if amount < 0:
            return False
        if self.accounts.get(sender.to_string().hex(), 0) < amount:
            print("Not enough in account: ")
            return False
        return sender.verify(sig, transaction.encode('utf-8'))
        
    def readHexTransaction(self, hexStr):
        amount = int(hexStr[:15], 16)
        sender = ecdsa.VerifyingKey.from_string(bytes.fromhex(hexStr[15:143]), curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
        recipient = ecdsa.VerifyingKey.from_string(bytes.fromhex(hexStr[143:]), curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
        return sender, recipient, amount

    def pushTransaction(self, hex_transaction, signature):
        valid = self.transactionIsValid(hex_transaction, signature)
        if valid: 
            self.transaction_pool.append((hex_transaction, signature))

    def set_pub_key(self, pub_key):
        self.pub_key = pub_key

    def addPeer(self, peer_node):
        self.peers.append(peer_node)

    def blockIsValid(self, block):
        if block.tryNonce(block.nonce) != block.hash:
            print("Invalid block hash!")
            return False
        # If this block doesn't follow the last valid block
        if block.height != 0 and (block.prevHash != self.lastBlockProcessed.hash 
                                    or block.height != self.lastBlockProcessed.height + 1):
            return False
        for (transaction, signature) in block.transactions["Regular"]:
            if not self.transactionIsValid(transaction, signature):
                return False
        return True

    def processBlock(self, block):
        if self.blockIsValid(block):
            self.settleTransactions(block)
            self.lastBlockProcessed = block
        else:
            print("Invalid block!")

    def syncChain(self):
        # Returns bool changesSynced
        if self.lastBlockProcessed is None:
            # If some blocks exist, process the genesis block
            if len(self.blockchain.blocks) != 0:
                self.processBlock(self.blockchain.blocks[0])
            # Otherwise, there are no changes to sync
            else:
                return False
        if self.lastBlockProcessed.height != self.blockchain.blocks[-1].height:
            for block in self.blockchain.blocks[self.lastBlockProcessed.height + 1:]:
                self.processBlock(block)
            return True
        return False

        
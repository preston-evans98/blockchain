from blockchain import Blockchain
from node import Node
from wallet import Wallet

if __name__ == '__main__':
    btc = Blockchain()
    alice_node = Node(btc)
    alice_node.name = "Alice"
    bob_node = Node(btc)
    bob_node.name = "Bob"
    alice = Wallet(alice_node)
    bob = Wallet(bob_node, new=True)

    btc.difficulty = 1
    alice_node.addPeer(bob_node)
    bob_node.addPeer(alice_node)

    alice_node.mineOneBlock()
    print(alice_node.accounts)
    alice.send(13, bob.pub_key)
    alice_node.mineOneBlock()
    bob_node.mineOneBlock()

    print(bob_node.accounts)
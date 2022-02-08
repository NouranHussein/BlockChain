import datetime
import hashlib
from pyvis.network import Network
import rsa

net = Network()
records_history = {}
difference = 2
difficulty = 19
attacker_computation_power = 40
allUser_computation_power = 60
rounds = 6
attack_Success = 0
ex = 0


def init_network(name, qt):
    records_history[name] = qt


def add_transaction(from_node, to_node, qt):
    records_history[from_node] -= qt
    records_history[to_node] += qt

    if records_history[from_node] < 0:
        return False
    else:
        return True


class Block:
    blockNo = 0
    data = None
    next = None
    nonce = 0
    previous_hash = 0x0
    timestamp = datetime.datetime.now()

    def __init__(self, msg):
        self.data = "-".join(msg)

    def hash(self):
        h = hashlib.sha256()
        h.update(
            str(self.nonce).encode('utf-8') +
            str(self.data).encode('utf-8') +
            str(self.previous_hash).encode('utf-8') +
            str(self.timestamp).encode('utf-8') +
            str(self.blockNo).encode('utf-8')
        )
        return h.hexdigest()

    def __str__(self):
        return "Block Hash: " + str(self.hash()) + "\nBlockNo: " + str(self.blockNo) + "\nNonce: " + str(
            self.nonce) + "\nprev Hashes: " + str(
            self.previous_hash) + "\n--------------"


class Node:
    privateKey = None
    publicKey = None

    def get_key(self):
        (self.publicKey, self.privateKey) = rsa.newkeys(1024)

    def verify_transaction(self, msg, sign):
        hash = rsa.verify(msg.encode("utf-8"), sign, self.publicKey)
        return hash

    def get_hash(self, msg):
        return rsa.compute_hash(msg.encode("utf-8"), 'SHA-512')

    def get_signature(self, msg):
        return rsa.sign(msg.encode("utf-8"), self.privateKey, 'SHA-512')


class Blockchain:
    count2 = 0
    maxNonce = 2 ** 32
    target = 2 ** (256 - difficulty)
    block = Block("Genesis")
    dummy = head = block
    freq = {}
    branch = False
    count = 0
    attack = 0
    block2 = None
    attacker_won = False
    user_won = False

    def add(self, block, flag):
        if flag is False:
            block.previous_hash = self.block.hash()
            block.blockNo = self.block.blockNo + 1
        elif flag is True:
            block.previous_hash = self.block2.hash()
            block.blockNo = self.block.blockNo + 1

    def mine(self, block, target):
        for n in range(self.maxNonce):
            if int(block.hash(), 16) <= self.target:

                if self.count - self.count2 >= difference and self.branch is True:
                    self.count = 0
                    self.count2 = 0
                    self.block = self.block2
                    self.block2 = None
                    self.attacker_won = True
                    self.branch = False
                    self.user_won = False
                    print("Attacker Branch succeed!!\n\n")
                    if ex == 1:
                        return

                elif self.count2 - self.count >= difference and self.branch is True:
                    self.branch = False
                    self.count = 0
                    self.count2 = 0
                    self.block2 = None
                    self.attacker_won = False
                    self.user_won = True
                    print("Main Branch succeed!!\n\n")

                if target in self.freq:

                    self.count += 1
                    self.attack += 1
                    if ex == 0:
                        net.add_node("Attacker block " + str(self.attack))

                    if block.blockNo != 1 and self.branch is False:
                        self.branch = True
                        if ex == 0:
                            net.add_edge("block " + str(self.block.blockNo), "Attacker block " + str(self.attack))
                        self.add(block, False)
                        print(block)
                        self.block2 = block

                    elif self.branch is True:
                        if ex == 0:
                            net.add_edge("Attacker block " + str(self.attack - 1), "Attacker block " + str(self.attack))
                        self.add(block, True)
                        print(block)
                        self.block2 = block
                else:
                    if self.branch is True:
                        self.count2 += 1
                    self.add(block, False)
                    self.freq[block] = 1
                    print(block)
                    if ex == 0:
                        net.add_node("block " + str(block.blockNo))
                    if block.blockNo != 1 and self.attacker_won is False:
                        if ex == 0:
                            net.add_edge("block " + str(self.block.blockNo), "block " + str(block.blockNo))
                    if block.blockNo != 1 and self.attacker_won:
                        if ex == 0:
                            net.add_edge("Attacker block " + str(self.attack), "block " + str(block.blockNo))
                        self.attacker_won = False

                break
            else:
                block.nonce += 1




blockchain = Blockchain()

t = ["Alice pays Bob 50 LD", "Bob pays Nai 50 LD", "Nai gets from Bob 50 LD", "Bob gets from Alice 50 LD"]
arr = ["alice", "bob", "nai"]
arr2 = ["alice", "bob", "bob", "nai", "bob", "nai", "alice", "bob"]
qt = [50, 50, 50, 50]

for n in range(3):
    init_network(arr[n], 100)

cont = True
for n in range(4):
    user = Node()
    user.get_key()
    sign = user.get_signature(t[n])
    h = user.get_hash(t[n])
    verified = user.verify_transaction(t[n], sign)
    if verified is False:
        cont = False
        print("transaction " + str(n) + " is not Authenticated")

for n in range(4):
    res = add_transaction(arr2[n], arr2[n + 1], qt[n])
    if res is False:
        cont = False
        print("there is overspending in transaction " + str(n + 1))

if cont is True:
    print("no overspending between transactions")
    print("transactions verified against integrity and Authentication")

    # attacker_speed = int(rounds / ((attacker_computation_power/100) * rounds))
    # user_speed = int(rounds / ((allUser_computation_power/100) * rounds))
    # print("attacker step " + str(attacker_speed))
    # print("user step " + str(user_speed))
    # s = 0
    # u = 0
    # for n in range(rounds+1):
    #     if s >= attacker_speed:
    #         k = Block([t[n % 4] + "attack" + str(n + 1)])
    #         blockchain.mine(k, blockchain.block)
    #         s = 0
    #     if u >= user_speed or n < 2:
    #         b = Block([t[n % 4]])
    #         blockchain.mine(b, blockchain.block.next)
    #         blockchain.block.next = b
    #         blockchain.block = blockchain.block.next
    #         u = 0
    #     u += 1
    #     s += 1
    #     net.show("blockchain.html")

    # attacker_computation_power = 10
    # allUser_computation_power = 90
    #
    # while attack_Success == 0:
    #     ex = 1
    #     testblockchain = Blockchain()
    #     attacker_speed = int(rounds / ((attacker_computation_power / 100) * rounds))
    #     user_speed = int(rounds / ((allUser_computation_power / 100) * rounds))
    #     s = 0
    #     u = 0
    #     print(attacker_speed)
    #     print(user_speed)
    #     for n in range(rounds):
    #         if s >= attacker_speed:
    #             k = Block([t[n % 4] + "attack" + str(n + 1)])
    #             testblockchain.mine(k, testblockchain.block)
    #             s = 0
    #         if u >= user_speed:
    #             b = Block([t[n % 4]])
    #             testblockchain.mine(b, testblockchain.block.next)
    #             testblockchain.block.next = b
    #             testblockchain.block = testblockchain.block.next
    #             u = 0
    #
    #         if testblockchain.attacker_won is True:
    #             attack_Success = 1
    #             break
    #         u += 1
    #         s += 1
    #
    #     if attacker_computation_power < 100 and allUser_computation_power > 10 and attack_Success == 0:
    #         attacker_computation_power += 5
    #         allUser_computation_power -= 5
    #     else:
    #         break
    #
    #     while testblockchain.head is not None:
    #         testblockchain.head = testblockchain.head.next
    #
    # print("Power of Attacker must be " + str(attacker_computation_power) + " to make successful attack.")

    import time
    while True:
        before = time.time()
        b = Block([t[n % 4]])
        blockchain.mine(b, blockchain.block.next)
        blockchain.block.next = b
        blockchain.block = blockchain.block.next
        after = time.time()
        diff = after - before
        print("difference: " + str(diff))
        print("Difficulty: " + str(difficulty))
        if diff > 1.6:
            difficulty -= 1
        elif diff < 0.6:
            difficulty += 1
        if (1.5 >= diff >= 0.5) or difficulty < 0:
            break
    print(difficulty)

    # while blockchain.head is not None:
    #     blockchain.head = blockchain.head.next


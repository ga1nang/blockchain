import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Backend.util.util import hash256


class BlockHeader:
    def __init__(self, version, prevBlockHash, merkleRoot, timestamp, bits):
        self.version = version
        self.prevBlockHash = prevBlockHash
        self.merkelRoot = merkleRoot
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = 0
        self.blockHash = ""
        
    def mine(self): 
        while (self.blockHash[:4]) != '0000':
            self.blockHash = hash256((str(self.version) + self.prevBlockHash + self.merkelRoot +
                                      str(self.timestamp) + self.bits + str(self.nonce)).encode()).hex()
            self.nonce += 1
        message = f"Mining started {self.nonce}"
        print(f"\r{message:<50}", end='', flush=True)




import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Blockchain.Backend.core.database.database import BlockChainDB
from Blockchain.Backend.util.util import (
    hash256,
    little_endian_to_int,
    int_to_little_endian,
    bits_to_target   
)    



class BlockHeader:
    def __init__(self, version, prevBlockHash, merkleRoot, timestamp, bits, nonce = None):
        self.version = version
        self.prevBlockHash = prevBlockHash
        self.merkleRoot = merkleRoot
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = nonce
        self.blockHash = ""
    
    
    @classmethod
    def parse(cls, s):
        version = little_endian_to_int(s.read(4))
        prevBlockHash = s.read(32)[::-1]
        merkleRoot = s.read(32)[::-1]
        timestamp = little_endian_to_int(s.read(4))
        bits = s.read(4)
        nonce = s.read(4)
        return cls(version, prevBlockHash, merkleRoot, timestamp, bits, nonce)
        
        
    def serialize(self):
        res = int_to_little_endian(self.version, 4)
        res += self.prevBlockHash[::-1]
        res += self.merkleRoot[::-1]
        res += int_to_little_endian(self.timestamp, 4)
        res += self.bits
        res += self.nonce
        return res    
        
        
    def mine(self, target): 
        self.blockHash = target + 1
        
        while self.blockHash > target:
            self.blockHash = little_endian_to_int(
                hash256(
                    int_to_little_endian(self.version, 4)
                    + bytes.fromhex(self.prevBlockHash)[::-1]
                    + bytes.fromhex(self.merkleRoot)[::-1]
                    + int_to_little_endian(self.timestamp, 4)
                    + self.bits
                    + int_to_little_endian(self.nonce, 4)
                )
            )
            self.nonce += 1
        message = f"Mining started {self.nonce}"
        #print(f"\r{message:<50}", end='\r', flush=True)
        self.blockHash = int_to_little_endian(self.blockHash, 32).hex()[::-1]
        self.nonce -= 1
        self.bits = self.bits.hex()


    def validateBlock(self):
        lastBlock = BlockChainDB().lastBlock()

        #first consensus rule
        #checking the received block should refer to the previous block
        #checking the previous block refer to the data in my db
        if self.prevBlockHash.hex() == lastBlock['BlockHeader']['blockHash']:
            #second check
            #proof of work
            #check independently
            if self.check_pow():
                return True
    
    
    def check_pow(self):
        sha = hash256(self.serialize())
        proof = little_endian_to_int(sha)
        #if true successfully solve the puzzle
        return proof < bits_to_target(self.bits)


    def generateBlockHash(self):
        sha = hash256(self.serialize())
        proof = little_endian_to_int(sha)
        return int_to_little_endian(proof, 32).hex()[::-1]
    
    
    def to_dict(self):
        dt = self.__dict__
        return dt

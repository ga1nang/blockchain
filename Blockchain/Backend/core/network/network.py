import sys
sys.path.append('E:\\subject\\Distributed_System\\bitcoin')

from io import BytesIO
from Blockchain.Backend.util.util import (
    int_to_little_endian,
    little_endian_to_int,
    hash256,
    encode_varint
)

NETWORK_MAGIC = b'\xf9\xbe\xb4\xd9'
#this value tell the end user finishing sending the data
FINISHED_SENDING =b'\x0a\x11\x09\x07'

#responsible for send data
class NetworkEnvelope:
    def __init__(self, command, payload):
        self.command = command
        self.payload = payload
        self.magic = NETWORK_MAGIC
        
    @classmethod
    def parse(cls, s):
        magic = s.read(4)
        
        if magic != NETWORK_MAGIC:
            raise RuntimeError(f"Magic is not right {magic.hex()} vs {NETWORK_MAGIC.hex()}")
        
        command = s.read(12)
        command = command.strip(b'\x00')
        payloadLen = little_endian_to_int(s.read(4))
        checksum = s.read(4)
        payload = s.read(payloadLen)
        calculatedChecksum = hash256(payload)[:4]
        
        if calculatedChecksum != checksum:
            raise IOError("Checksum does not match")
        
        return cls(command, payload)
        
        
    def serialize(self):
        res = self.magic
        res += self.command + b'\x00' * (12 - len(self.command))
        res += int_to_little_endian(len(self.payload), 4)
        res += hash256(self.payload)[:4]
        res += self.payload
        return res


    def stream(self):
        return BytesIO(self.payload)


class requestBlock:
    #command to request what kind of data
    command = b'requestBlock'
    
    def __init__(self, startBlock = None, endBlock = None):
        if startBlock is None:
            raise RuntimeError("Starting block cannot be None")
        else:
            self.startBlock = startBlock
            
        #check if this is a new miner or old miner
        if endBlock is None:
            self.endBlock = b'\x00' * 32
        else:
            self.endBlock = endBlock
            
            
    #parse the received data
    @classmethod
    def parse(cls, stream):
        startBlock = stream.read(32)
        endBlock = stream.read(32)
        return startBlock, endBlock
            
    
    #send data through network we need to serialize it
    def serialize(self):
        res = self.startBlock
        res += self.endBlock
        return res
    
    
class FinishedSending:
    command = b'Finished'
    
    @classmethod
    def parse(cls, s):
        magic = s.read(4)
        
        if magic == FINISHED_SENDING:
            return "Finished"
        
    
    def serialize(self):
        res = FINISHED_SENDING
        return res
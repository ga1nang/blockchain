from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.core.Tx import Tx
from Blockchain.Backend.util.util import (
    little_endian_to_int,
    int_to_little_endian,
    encode_varint
)

class Block:
    def __init__(self, Height, Blocksize, BlockHeader, TxCount, Txs):
        self.Height = Height
        self.Blocksize = Blocksize
        self.BlockHeader = BlockHeader
        self.TxCount = TxCount
        self.Txs = Txs
        
        
    def serialize(self):
        result = int_to_little_endian(self.Height, 4)
        result += int_to_little_endian(self.Blocksize, 4)
        result += self.BlockHeader.serialize()
        result += encode_varint(len(self.Txs))

        for tx in self.Txs:
            result += tx.serialize()
        
        return result
    
    
    @classmethod
    def to_obj(cls, lastblock):
        block = BlockHeader(lastblock['BlockHeader']['version'],
                    bytes.fromhex(lastblock['BlockHeader']['prevBlockHash']),
                    bytes.fromhex(lastblock['BlockHeader']['merkleRoot']),
                    lastblock['BlockHeader']['timestamp'],
                    bytes.fromhex(lastblock['BlockHeader']['bits']))
        
        block.nonce = int_to_little_endian(lastblock['BlockHeader']['nonce'], 4)

        Transactions = []
        for tx in lastblock['Txs']:
            Transactions.append(Tx.to_obj(tx))
        
        block.blockHash = bytes.fromhex(lastblock['BlockHeader']['blockHash'])
        return cls(lastblock['Height'], lastblock['Blocksize'], block, len(Transactions), Transactions)
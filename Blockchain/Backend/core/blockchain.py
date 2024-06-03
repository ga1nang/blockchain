import sys
sys.path.append('E:\\subject\\Distributed_System\\bitcoin')

from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import hash256
from Blockchain.Backend.core.database.database import BlockChainDB
from Blockchain.Backend.core.Tx import CoinbaseTx
from multiprocessing import Process, Manager
from Blockchain.Frontend.run import main

import time

ZERO_HASH = '0' * 64
VERSION = 1

class Blockchain:
    def __init__(self, utxos):
        self.utxos = utxos
        
    def GenesisBlock(self):
        BlockHeight = 0
        prevBlockHash = ZERO_HASH
        self.addBlock(BlockHeight, prevBlockHash)
        
    def write_on_disk(self, block):
        blockchainDB = BlockChainDB()
        blockchainDB.write(block)
        
    def fetch_last_block(self):
        blockchainDB = BlockChainDB()
        return blockchainDB.lastBlock()
    
    
    
    
    #keep track of all the unspent Transaction in cache memory for fast retrival
    def store_utxos_in_cache(self, Transaction):
        self.utxos[Transaction.TxId] = Transaction
    
        
    def addBlock(self, BlockHeight, prevBlockHash):
        timestamp = int(time.time())
        coinBaseInstance = CoinbaseTx(BlockHeight)
        coinBaseTx = coinBaseInstance.CoinbaseTransaction()
        merkelRoot= coinBaseTx.TxId
        bits = "ffff001f"
        blockheader = BlockHeader(VERSION, prevBlockHash, merkelRoot, timestamp, bits)
        blockheader.mine()
        
        self.store_utxos_in_cache(coinBaseTx)
        self.write_on_disk([Block(BlockHeight, 1, blockheader.__dict__, 1, coinBaseTx.to_dict()).__dict__])
        
    def main(self):
        lastBlock = self.fetch_last_block()
        if lastBlock is None:
            self.GenesisBlock()
        while True:
            lastBlock = self.fetch_last_block()
            BlockHeight = lastBlock["Height"] + 1
            prevBlockHash = lastBlock["BlockHeader"]["blockHash"]
            self.addBlock(BlockHeight, prevBlockHash)
        
if __name__ == "__main__":
    with Manager() as manager:
        utxos = manager.dict()
        
        webapp = Process(target=main, args=(utxos,))
        webapp.start()
        
        blockchain = Blockchain(utxos)
        blockchain.main()
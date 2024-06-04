import sys
sys.path.append('E:\\subject\\Distributed_System\\bitcoin')

from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import hash256, merkle_root
from Blockchain.Backend.core.database.database import BlockChainDB
from Blockchain.Backend.core.Tx import CoinbaseTx
from multiprocessing import Process, Manager
from Blockchain.Frontend.run import main

import time

ZERO_HASH = '0' * 64
VERSION = 1

class Blockchain:
    def __init__(self, utxos, MemPool):
        self.utxos = utxos
        self.MemPool = MemPool
        
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
    def store_utxos_in_cache(self):
        for tx in self.addTransactionsInBlock:
            print(f"Transaction added {tx.TxId}")
            self.utxos[tx.TxId] = tx
    
    
    def remove_spent_Transactions(self):
        for txId_index in self.remove_spent_transactions:
            if txId_index[0].hex() in self.utxos:
                
                if len(self.utxos[txId_index[0].hex()].tx_outs) < 2:
                    print(f"Spent Transaction removed {txId_index[0].hex()}")
                    del self.utxos[txId_index[0].hex()]
                else:
                    prev_trans = self.utxos[txId_index[0].hex()]
                    self.utxos[txId_index[0].hex()] = prev_trans.tx_outs.pop(txId_index[1])
     
    
    #Read transaction from Memory Pool
    def read_transaction_from_memorypool(self):
        self.TxIds = []
        self.addTransactionsInBlock = []
        self.remove_spent_transactions = []

        for tx in self.MemPool:
            self.TxIds.append(bytes.fromhex(tx))
            self.addTransactionsInBlock.append(self.MemPool[tx])
            
            for spent in self.MemPool[tx].tx_ins:
                self.remove_spent_transactions.append([spent.prev_tx, spent.prev_index])
            
    
    #remove confirmed transactions from memory pool
    def remove_transaction_from_memorypool(self):
        for tx in self.TxIds:
            if tx.hex() in self.MemPool:
                del self.MemPool[tx.hex()]
            
    def convert_to_json(self):
        self.TxJson = []
        
        for tx in self.addTransactionsInBlock:
            self.TxJson.append(tx.to_dict())
        
    
    def calculate_fee(self):
        self.input_amount = 0
        self.output_amount = 0
        #Calculate Input Amount
        for TxId_index in self.remove_spent_transactions:
            if TxId_index[0].hex() in self.utxos:
                self.input_amount += (
                    self.utxos[TxId_index[0].hex()].tx_outs[TxId_index[1]].amount
                )

        #Calculate Output Amount
        for tx in self.addTransactionsInBlock:
            for tx_out in tx.tx_outs:
                self.output_amount += tx_out.amount

        self.fee = self.input_amount - self.output_amount
    
    def addBlock(self, BlockHeight, prevBlockHash):
        self.read_transaction_from_memorypool()
        self.calculate_fee()
        timestamp = int(time.time())
        coinBaseInstance = CoinbaseTx(BlockHeight)
        coinBaseTx = coinBaseInstance.CoinbaseTransaction()
        
        coinBaseTx.tx_outs[0].amount = coinBaseTx.tx_outs[0].amount + self.fee
        #print(f"Fee is {self.fee}")
        
        self.TxIds.insert(0, bytes.fromhex(coinBaseTx.id()))
        self.addTransactionsInBlock.insert(0, coinBaseTx)
        
        merkelRoot = merkle_root(self.TxIds)[::-1].hex()
        bits = "ffff001f"
        blockheader = BlockHeader(VERSION, prevBlockHash, merkelRoot, timestamp, bits)
        blockheader.mine()
        self.remove_spent_Transactions()
        self.remove_transaction_from_memorypool()
        print(f"{BlockHeight}")
        
        self.store_utxos_in_cache()
        self.convert_to_json()
        self.write_on_disk([Block(BlockHeight, 1, blockheader.__dict__, 1, self.TxJson).__dict__])
        
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
        MemPool = manager.dict()
        
        webapp = Process(target=main, args=(utxos, MemPool))
        webapp.start()
        
        blockchain = Blockchain(utxos, MemPool)
        blockchain.main()
import sys
sys.path.append('E:\\subject\\Distributed_System\\p2p\\p2p_test_1_commit')

import configparser
from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import hash256, merkle_root, target_to_bits
from Blockchain.Backend.core.database.database import BlockChainDB, NodeDB
from Blockchain.Backend.core.Tx import CoinbaseTx
from multiprocessing import Process, Manager
from Blockchain.Frontend.run import main
from Blockchain.Backend.core.network.syncManager import syncManager

import time

ZERO_HASH = '0' * 64
VERSION = 1
INITIAL_TARGET = 0x0000FFFF00000000000000000000000000000000000000000000000000000000

class Blockchain:
    def __init__(self, utxos, MemPool):
        self.utxos = utxos
        self.MemPool = MemPool
        self.current_target = INITIAL_TARGET
        self.bits = target_to_bits(INITIAL_TARGET)
    
        
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
    
    
    def startSync(self, localHost, localPort):
        config = configparser.ConfigParser()
        config.read('config.ini')
        nodeIPs = [config['NODES'][key] for key in config['NODES']]
        
        for nodeIP in nodeIPs:
            if nodeIP != localHost:
                sync = syncManager(localHost, localPort, nodeIP)
                sync.startDownload()
    
    
    #keep track of all the unspent Transaction in cache memory for fast retrival
    def store_utxos_in_cache(self):
        for tx in self.addTransactionsInBlock:
            #print(f" {tx.TxId}")
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
        self.Blocksize = 80
        self.TxIds = []
        self.addTransactionsInBlock = []
        self.remove_spent_transactions = []

        for tx in self.MemPool:
            self.TxIds.append(bytes.fromhex(tx))
            self.addTransactionsInBlock.append(self.MemPool[tx])
            self.Blocksize += len(self.MemPool[tx].serialize())
            
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
        self.Blocksize += len(coinBaseTx.serialize())
        
        coinBaseTx.tx_outs[0].amount = coinBaseTx.tx_outs[0].amount + self.fee
        #print(f"Fee is {self.fee}")
        
        self.TxIds.insert(0, bytes.fromhex(coinBaseTx.id()))
        self.addTransactionsInBlock.insert(0, coinBaseTx)
        
        merkelRoot = merkle_root(self.TxIds)[::-1].hex()

        blockheader = BlockHeader(VERSION, prevBlockHash, merkelRoot, timestamp, self.bits)
        blockheader.mine(self.current_target)
        self.remove_spent_Transactions()
        self.remove_transaction_from_memorypool()
        #print(f"{BlockHeight}")
        
        self.store_utxos_in_cache()
        self.convert_to_json()
        self.write_on_disk(
            [
                Block(
                    BlockHeight, self.Blocksize, blockheader.__dict__, len(self.TxJson), self.TxJson
                ).__dict__
            ]
        )
        
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
    config = configparser.ConfigParser()
    config.read('config.ini')
    localHost = config['DEFAULT']['host']
    localPort = int(config['MINER']['port'])                                                                                                                                                                                                  
    webPort = int(config['Webhost']['port'])

    with Manager() as manager:
        utxos = manager.dict()
        MemPool = manager.dict()
        
        otherHost = '172.20.10.2'
        
        sync = syncManager(localHost, localPort, otherHost)
        startServer = Process(target=sync.spinUpTheServer)
        startServer.start()
        
        blockchain = Blockchain(utxos, MemPool)
        blockchain.startSync(localHost, localPort)
        blockchain.main()
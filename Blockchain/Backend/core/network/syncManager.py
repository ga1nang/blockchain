import sys
sys.path.append('E:\\subject\\Distributed_System\\bitcoin')

from Blockchain.Backend.core.network.connection import Node
from Blockchain.Backend.core.database.database import BlockChainDB

class syncManager:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
        
    def spinUpTheServer(self):
        self.server = Node(self.host, self.port)
        self.server.startServer()
        print("SERVER STARTED")
        print(f"[LISTENING] at {self.host}:{self.port}")
        
        
    def startDownload(self, port):
        lastBlock = BlockChainDB().lastBlock()
        
        if not lastBlock:
            lastBlockHeader = "0000b5d81ae7d5d1081a158158ce7a2bd56fbd922ecd5fe25199d2c32be5a690"
        else:
            lastBlockHeader = lastBlock['BlockHeader']['blockHash']
            
        startBlock = bytes.fromhex(lastBlockHeader)
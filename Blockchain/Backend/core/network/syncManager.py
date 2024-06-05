import sys
sys.path.append('E:\\subject\\Distributed_System\\bitcoin')

from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.network.connection import Node
from Blockchain.Backend.core.database.database import BlockChainDB, NodeDB 
from Blockchain.Backend.core.network.network import requestBlock, NetworkEnvelope, FinishedSending, portlist
from Blockchain.Backend.util.util import little_endian_to_int
from threading import Thread

class syncManager:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
        
    def spinUpTheServer(self):
        self.server = Node(self.host, self.port)
        self.server.startServer()
        print("SERVER STARTED")
        print(f"[LISTENING] at {self.host}:{self.port}")
        
        while True:
            self.conn, self.addr = self.server.acceptConnection()
            handleConn = Thread(target = self.handleConnection)
            handleConn.start()
        
        
    def handleConnection(self):
        envelope = self.server.read()
        
        try:
            if len(str(self.addr[1])) == 4:
                self.addNode()
            
            if envelope.command == requestBlock.command:
                start_block, end_block = requestBlock.parse(envelope.stream())
                self.sendBlockToRequestor(start_block)
                print(f"Start Block is {start_block} \n End Block is {end_block}")
        except Exception as e:
            print(f"Error while processing the client request \n {e}")
     
    
    def addNode(self):
        nodeDb = NodeDB()
        portList = nodeDb.read()

        if self.addr[1] and (self.addr[1] + 1) not in portList:
            nodeDb.write([self.addr[1] + 1])
    
     
    def sendBlockToRequestor(self, start_block):
        blocksToSend = self.fetchBlocksFromBlockchain(start_block)

        try:
            self.sendBlock(blocksToSend)
            #self.sendSecondryChain()
            self.sendPortlist()
            self.sendFinishedMessage()
        except Exception as e:
            print(f"Unable to send the blocks \n {e}")
    
    
    def sendPortlist(self):
        nodeDB = NodeDB()
        portLists = nodeDB.read()

        portLst = portlist(portLists)
        envelope = NetworkEnvelope(portLst.command, portLst.serialize())
        self.conn.sendall(envelope.serialize())
    
    
    def sendFinishedMessage(self):
        MessageFinish = FinishedSending()
        envelope = NetworkEnvelope(MessageFinish.command, MessageFinish.serialize())
        self.conn.send(envelope.serialize())
    
    
    def sendBlock(self, blockstoSend):
        for block in blockstoSend:
            cblock = Block.to_obj(block)
            envelope = NetworkEnvelope(cblock.command, cblock.serialize())
            self.conn.sendall(envelope.serialize())
            print(f"Block Sent {cblock.Height}")
                
        
    def fetchBlocksFromBlockchain(self, start_Block):
        fromBlocksOnwards = start_Block.hex()

        blocksToSend = []
        blockchain = BlockChainDB()
        blocks = blockchain.read()

        foundBlock = False 
        for block in blocks:
            if block['BlockHeader']['blockHash'] == fromBlocksOnwards:
                foundBlock = True
                continue
        
            if foundBlock:
                blocksToSend.append(block)
        
        return blocksToSend
        
        
    def startDownload(self, localhost, port):
        lastBlock = BlockChainDB().lastBlock()
        
        if not lastBlock:
            lastBlockHeader = "0000b5d81ae7d5d1081a158158ce7a2bd56fbd922ecd5fe25199d2c32be5a690"
        else:
            lastBlockHeader = lastBlock['BlockHeader']['blockHash']
            
        startBlock = bytes.fromhex(lastBlockHeader)
        
        getHeaders = requestBlock(startBlock=startBlock)
        self.connect = Node(self.host, port)
        self.socket = self.connect.connect(localhost)
        self.stream = self.socket.makefile('rb', None)
        self.connect.send(getHeaders)
        
        while True:    
            envelope = NetworkEnvelope.parse(self.stream)
            
            if envelope.command == b'Finished':
                print(f"All Blocks Received")
                self.socket.close()
                break
            
            
            if envelope.command == b'portlist':
                ports = portlist.parse(envelope.stream())
                nodeDb = NodeDB()
                portlists = nodeDb.read()

                for port in ports:
                    if port not in portlists:
                        nodeDb.write([port])
            
                
            if envelope.command == b'block':
                blockObj = Block.parse(envelope.stream())
                BlockHeaderObj = BlockHeader(blockObj.BlockHeader.version,
                            blockObj.BlockHeader.prevBlockHash, 
                            blockObj.BlockHeader.merkleRoot, 
                            blockObj.BlockHeader.timestamp,
                            blockObj.BlockHeader.bits,
                            blockObj.BlockHeader.nonce)
                
                if BlockHeaderObj.validateBlock():
                    for idx, tx in enumerate(blockObj.Txs):
                        tx.TxId = tx.id()
                        blockObj.Txs[idx] = tx.to_dict()
                
                    BlockHeaderObj.blockHash = BlockHeaderObj.generateBlockHash()
                    BlockHeaderObj.prevBlockHash = BlockHeaderObj.prevBlockHash.hex()
                    BlockHeaderObj.merkleRoot = BlockHeaderObj.merkleRoot.hex()
                    BlockHeaderObj.nonce =  little_endian_to_int(BlockHeaderObj.nonce)
                    BlockHeaderObj.bits = BlockHeaderObj.bits.hex()
                    blockObj.BlockHeader = BlockHeaderObj
                    BlockChainDB().write([blockObj.to_dict()])
                    print(f"Block Received - {blockObj.Height}")
                else:
                    print(f"Chain is broken")
            
        
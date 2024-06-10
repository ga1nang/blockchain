import socket
from threading import Thread
from Blockchain.Backend.core.network.network import NetworkEnvelope, requestBlock, FinishedSending
from Blockchain.Backend.core.database.database import BlockChainDB
from Blockchain.Backend.core.block import Block

class syncManager:
    def __init__(self, localHost, localPort, remoteHost):
        self.localHost = localHost
        self.localPort = localPort
        self.remoteHost = remoteHost

    def spinUpTheServer(self):
        self.server = Node(self.localHost, self.localPort)
        self.server.startServer()
        print("SERVER STARTED")
        print(f"[LISTENING] at {self.localHost}:{self.localPort}")
        
        while True:
            self.conn, self.addr = self.server.acceptConnection()
            handleConn = Thread(target=self.handleConnection)
            handleConn.start()

    def handleConnection(self):
        envelope = self.server.read()
        try:
            if envelope.command == requestBlock.command:
                start_block, end_block = requestBlock.parse(envelope.stream())
                self.sendBlockToRequestor(start_block)
                print(f"Start Block is {start_block} \nEnd Block is {end_block}")
        except Exception as e:
            print(f"Error while processing the client request\n{e}")
            
            
    def sendBlockToRequestor(self, start_block):
        blocksToSend = self.fetchBlocksFromBlockchain(start_block)

        try:
            self.sendBlock(blocksToSend)
            #self.sendSecondryChain()
            #self.sendPortlist()
            self.sendFinishedMessage()
        except Exception as e:
            print(f"Unable to send the blocks \n {e}")
            
            
    def sendFinishedMessage(self):
        MessageFinish = FinishedSending()
        envelope = NetworkEnvelope(MessageFinish.command, MessageFinish.serialize())
        self.conn.sendall(envelope.serialize())
            
            
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
    

    def startDownload(self):
        lastBlock = BlockChainDB().lastBlock()
        
        if not lastBlock:
            lastBlockHeader = "0000503b6de3f475e410bc7ad11b480f8fb7c36cab8539ee28955851517a36ee"
        else:
            lastBlockHeader = lastBlock["BlockHeader"]["blockHash"]
            
        startBlock = bytes.fromhex(lastBlockHeader)
        
        getHeaders = requestBlock(startBlock=startBlock)
        self.connect = Node(self.remoteHost, self.localPort)
        self.socket = self.connect.connect(self.remoteHost, self.localPort)
        self.connect.send(getHeaders)

class Node:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ADDR = (self.host, self.port)

    def startServer(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        self.server.listen()

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket

    def acceptConnection(self):
        self.conn, self.addr = self.server.accept()
        self.stream = self.conn.makefile('rb', None)
        print(f"Accepted.....{self.addr}")
        return self.conn, self.addr

    def closeConnection(self):
        self.socket.close()

    def send(self, message):
        envelope = NetworkEnvelope(message.command, message.serialize())
        self.socket.sendall(envelope.serialize())

    def read(self):
        envelope = NetworkEnvelope.parse(self.stream)
        return envelope

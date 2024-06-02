import sys
sys.path.append('E:\\subject\\Distributed_System\\bitcoin')

from Blockchain.Backend.util.util import int_to_little_endian, encode_varint

class Script:
    def __init__(self, cmds = None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds   
    
    def serialize(self):
        result = b""
        for cmd in self.cmds:
            #if cmd is an int, it's an opcode
            #else it's element
            if type(cmd) == int:
                result += int_to_little_endian(cmd, 1)
            else:
                length = len(cmd)
                if length < 75:
                    result += int_to_little_endian(length, 1)
                elif length > 75 and length < 0x100:
                    # 76 is pushdata1
                    result += int_to_little_endian(76, 1)
                    result += int_to_little_endian(length, 1)
                elif length >= 0x100 and length <= 520:
                    # 77 is pushdata2
                    result += int_to_little_endian(77, 1)
                    result += int_to_little_endian(length, 2)
                else:
                    raise ValueError("too long an cmd")

                result += cmd
                
        total = len(result)
        return encode_varint(total) + result   
    
    @classmethod
    def p2pkh_script(cls, h160):
        #Take a hash160 and return the p2pkh ScriptPubKey
        return Script([0x76, 0xa9, h160, 0x88, 0xac])
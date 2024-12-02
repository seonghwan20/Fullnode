import hashlib
import ecdsa
from itertools import combinations


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Stack:
    def __init__(self):
        self.top = None

    def PUSH(self, data):
        if self.top is None:
            self.top = Node(data)
        else:
            node = Node(data)
            node.next = self.top
            self.top = node

    def POP(self):
        if self.top is None:
            return None
        node = self.top
        self.top = self.top.next
        return node.data

    def PEEK(self):
        return None if self.top is None else self.top.data

    def IS_EMPTY(self):
        return self.top is None

    def DUP(self):
        if self.top:
            self.PUSH(self.top.data)

    def HASH(self, script_type):
        if self.top:
            node = self.POP()
            if script_type == "P2SH":
                self.PUSH(node)
                data_hash = hashlib.sha256(str(node).encode('utf-8')).hexdigest()
                self.PUSH(data_hash)
            else:
                data_hash = hashlib.sha256(bytes.fromhex(node)).hexdigest()
                self.PUSH(data_hash)

    def EQUAL(self):
        if self.top:
            data_1, data_2 = self.POP(), self.POP()
            self.PUSH(data_1 == data_2)

    def EQUALVERIFY(self):
        if self.top:
            data_1, data_2 = self.POP(), self.POP()
            if data_1 != data_2:
                return None

    def CHECKSIG(self, txid):
        if self.top and self.top.next:
            pubKey, sig = self.POP(), self.POP()
            try:
                result = sig_verify(sig, pubKey, txid)
                self.PUSH(result)
            except Exception:
                self.PUSH(False)

    def CHECKSIGVERIFY(self, txid):
        if self.top and self.top.next:
            pubKey, sig = self.POP(), self.POP()
            try:
                result = sig_verify(sig, pubKey, txid)
                self.PUSH(result)
            except Exception:
                self.PUSH(False)

    def CHECKMULTISIG(self, txid):
        N = int(self.POP())
        pubKey_list = [self.POP() for _ in range(N)]
        M = int(self.POP())
        sig_list = [self.POP() for _ in range(M)]

        combinations_list = list(combinations(pubKey_list, M))
        match = False
        for comb in combinations_list:
            count = 0
            for sig in sig_list:
                for pubKey in comb:
                    if sig_verify(sig, pubKey, txid):
                        count += 1
            if count == M:
                match = True
                break

        self.PUSH(match)

    def CHECKMULTISIGVERIFY(self, txid):
        N = int(self.POP())
        pubKey_list = [self.POP() for _ in range(N)]
        M = int(self.POP())
        sig_list = [self.POP() for _ in range(M)]

        combinations_list = list(combinations(pubKey_list, M))
        match = False
        for comb in combinations_list:
            count = 0
            for sig in sig_list:
                for pubKey in comb:
                    if sig_verify(sig, pubKey, txid):
                        count += 1
            if count == M:
                match = True
                break

    def CHECKFINALRESULT(self):
        return self.top is not None and self.top.next is None and self.top.data is True

    def script_verify(self, locking_script, unlocking_script, txid, unlocking_script_without_redeem_script, redeem_script):
        script_type = None
        if locking_script.split(' ')[-1] == "CHECKSIG":
            script_type = "P2PKH"
        elif locking_script.split(' ')[-1] == "EQUAL":
            script_type = "P2SH"
        elif locking_script.split(' ')[-1] == "CHECKMULTISIG":
            script_type = "MULTISIG"

        OP = {
            "DUP": Stack.DUP,
            "HASH": Stack.HASH,
            "EQUAL": Stack.EQUAL,
            "EQUALVERIFY": Stack.EQUALVERIFY,
            "CHECKSIG": Stack.CHECKSIG,
            "CHECKSIGVERIFY": Stack.CHECKSIGVERIFY,
            "CHECKMULTISIG": Stack.CHECKMULTISIG,
            "CHECKMULTISIGVERIFY": Stack.CHECKMULTISIGVERIFY,
            "CHECKFINALRESULT": Stack.CHECKFINALRESULT,
        }

        if script_type == "P2PKH":
            unlocking_script_data = unlocking_script.split(" ")
            for data in unlocking_script_data:
                self.PUSH(data)

            locking_script_data = locking_script.split(" ")
            for data in locking_script_data:
                if data in OP:
                    if data in ["CHECKSIG", "CHECKSIGVERIFY", "CHECKMULTISIG", "CHECKMULTISIGVERIFY"]:
                        OP[data](self, txid)
                    elif data == "HASH":
                        OP[data](self, script_type)
                    else:
                        OP[data](self)
                else:
                    self.PUSH(data)

        elif script_type == "MULTISIG":
            unlocking_script_data = unlocking_script.split(" ")
            for data in unlocking_script_data:
                self.PUSH(data)

            locking_script_data = locking_script.split(" ")
            for data in locking_script_data:
                if data in OP:
                    if data in ["CHECKSIG", "CHECKSIGVERIFY", "CHECKMULTISIG", "CHECKMULTISIGVERIFY"]:
                        OP[data](self, txid)
                    elif data == "HASH":
                        OP[data](self, script_type)
                    else:
                        OP[data](self)
                else:
                    self.PUSH(data)

        elif script_type == "P2SH":
            try:
                for data in unlocking_script_without_redeem_script.split(" "):
                    self.PUSH(data)
                self.PUSH(redeem_script)

                for data in locking_script.split(" "):
                    if data in OP:
                        if data in ["CHECKSIG", "CHECKSIGVERIFY", "CHECKMULTISIG", "CHECKMULTISIGVERIFY"]:
                            OP[data](self, txid)
                        elif data == "HASH":
                            OP[data](self, script_type)
                        else:
                            OP[data](self)
                    else:
                        self.PUSH(data)
                if self.POP():
                    i = 0
                    redeem_script = self.POP().split(" ")
                    while i < len(redeem_script):
                        data = redeem_script[i]
                        if data == "IF":
                            if int(self.POP()):
                                i += 1
                                continue
                            else:
                                while redeem_script[i] not in ["ELSE", "ENDIF"]:
                                    i += 1
                                i += 1
                                continue
                        elif data == "ENDIF":
                            if i == len(redeem_script):
                                return self
                            else:
                                i += 1
                                continue
                        elif data in OP:
                            if data in ["CHECKSIG", "CHECKSIGVERIFY", "CHECKMULTISIG", "CHECKMULTISIGVERIFY"]:
                                OP[data](self, txid)
                            elif data == "HASH":
                                OP[data](self, script_type)
                            else:
                                OP[data](self)
                        else:
                            self.PUSH(data)
                        i += 1
                else:
                    return False
            except Exception:
                return False

        return self


def sig_verify(sig, pubKey, txid):
    try:
        sig_bytes = bytes.fromhex(sig)
        pubKey_bytes = bytes.fromhex(pubKey)
        txid_bytes = bytes.fromhex(txid)

        private_key = ecdsa.SigningKey.from_string(sig_bytes, curve=ecdsa.SECP256k1)
        signature = private_key.sign(txid_bytes)

        public_key = ecdsa.VerifyingKey.from_string(pubKey_bytes, curve=ecdsa.SECP256k1)
        return public_key.verify(signature, txid_bytes)
    except Exception:
        return False

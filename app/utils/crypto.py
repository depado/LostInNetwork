# -*- coding: utf-8 -*-

import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random


class AESCipher:
    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(AESCipher.str_to_bytes(key)).digest()

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b''.decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * AESCipher.str_to_bytes(chr(self.bs - len(s) % self.bs))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, raw):
        raw = self._pad(AESCipher.str_to_bytes(raw))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)).decode('utf-8')

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')


def encrypt_string_from_master_password(data, password):
    ccipher = AESCipher(key=password)
    return ccipher.encrypt(data)


def decrypt_string_from_master_password(data, password):
    ccipher = AESCipher(key=password)
    return ccipher.decrypt(data)


def encrypt_file_from_master_password(fname, password):
    ccipher = AESCipher(key=password)
    with open(fname, "r+") as fd:
        data = ccipher.encrypt(fd.read())
        fd.seek(0)
        fd.write(data)
        fd.truncate()


def decrypt_file_from_master_password(fname, password):
    ccipher = AESCipher(key=password)
    with open(fname, "r+") as fd:
        data = ccipher.decrypt(fd.read())
        fd.seek(0)
        fd.write(data)
        fd.truncate()

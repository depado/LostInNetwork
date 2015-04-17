# -*- coding: utf-8 -*-

import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA512

from flask import session

from app import app


class AESCipher(object):
    """
    A classical AES Cipher. Can use any size of data and any size of password thanks to padding.
    Also ensure the coherence and the type of the data with a unicode to byte converter.
    """
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


class PasswordManager(object):

    @staticmethod
    def set_session_pwdh(clear_text_pwd):
        """
        Sets the session password hash so it can get used for later encryption/decryption
        :param clear_text_pwd: The password in clear-text (Won't be kept in the session obviously)
        """
        session['pwdh'] = PasswordManager.generate_pwdh_from_password(clear_text_pwd)

    @staticmethod
    def generate_pwdh_from_password(clear_text_pwd):
        m = SHA512.new()
        m.update(AESCipher.str_to_bytes(app.config.get('PWD_SALT')))
        m.update(AESCipher.str_to_bytes(clear_text_pwd))
        return m.hexdigest()

    @staticmethod
    def pop_session_pwdh():
        """
        Destroys the session password hash
        """
        session.pop('pwdh', None)

    @staticmethod
    def get_session_pwdh():
        """
        Returns the session password hash that can be used to encrypt and decrypt.
        """
        return session['pwdh'] if 'pwdh' in session else None

    @staticmethod
    def encrypt_string(data, key):
        """
        Encrypts a string using the AES Cipher.
        :param data: The string to encrypt.
        :param key: The key to encrypt the string.
        :return: The encrypted string.
        """
        ccipher = AESCipher(key=key)
        return ccipher.encrypt(data)

    @staticmethod
    def decrypt_string(data, key):
        """
        Decrypts a string using the AES Cipher.
        :param data: The encrypted string to be decrypted.
        :param key: The key used to decrypt the string (used to encrypt it before).
        :return: The decrypted string.
        """
        ccipher = AESCipher(key=key)
        return ccipher.decrypt(data)

    @staticmethod
    def encrypt_file(fname, key, overwrite=True):
        """
        Encrypts a file and overwrites it in the process with encrypted data or create another file for those data.
        :param fname: The path to the file.
        :param key: The key to encrypt the file.
        :param overwrite: Tells if the file should be overwritten.
        """
        ccipher = AESCipher(key=key)
        mode = "r+" if overwrite else "r"
        with open(fname, mode) as fd:
            data = ccipher.encrypt(fd.read())
            if overwrite:
                fd.seek(0)
                fd.write(data)
                fd.truncate()
        if not overwrite:
            with open("{}.out".format(fname), "w") as fd_out:
                fd_out.write(data)
                fd_out.truncate()

    @staticmethod
    def decrypt_file(fname, key, overwrite=True):
        """
        Decrypts a file and overwrites it with decrypted data or create another file for those data.
        :param fname: The path to the file.
        :param key: The key to decrypt the file.
        :param overwrite: Tells if the file should be overwritten.
        """
        ccipher = AESCipher(key=key)
        mode = "r+" if overwrite else "r"
        with open(fname, mode) as fd:
            data = ccipher.decrypt(fd.read())
            if overwrite:
                fd.seek(0)
                fd.write(data)
                fd.truncate()
        if not overwrite:
            with open("{}.out".format(fname), "w") as fd_out:
                fd_out.write(data)
                fd_out.truncate()

    @staticmethod
    def encrypt_string_from_session_pwdh(data):
        """
        Encrypts the data with the password hash stored in the session (if it exists)
        :param data: The data to encrypt.
        :return: The encrypted data or None if the password hash isn't stored in the session.
        """
        pwdh = PasswordManager.get_session_pwdh()
        if pwdh:
            return PasswordManager.encrypt_string(data, pwdh)
        else:
            return None

    @staticmethod
    def decrypt_string_from_session_pwdh(data):
        """
        Decrypts the data with the password hash stored in the session (if it exists)
        :param data: The data to decrypt.
        :return: The decrypted data or None if the password hash isn't stored in the session.
        """
        pwdh = PasswordManager.get_session_pwdh()
        if pwdh:
            return PasswordManager.decrypt_string(data, pwdh)
        else:
            return None

    @staticmethod
    def encrypt_file_from_session_pwdh(fname):
        """
        Encrypts the file with the password hash stored in the session (if it exists)
        :param fname: The path of the file to encrypt.
        """
        pwdh = PasswordManager.get_session_pwdh()
        if pwdh:
            PasswordManager.encrypt_file(fname, pwdh)

    @staticmethod
    def decrypt_file_from_session_pwdh(fname):
        """
        Decrypts the file with the password hash stored in the session (if it exists)
        :param fname: The path of the file to decrypt.
        """
        pwdh = PasswordManager.get_session_pwdh()
        if pwdh:
            PasswordManager.decrypt_file(fname, pwdh)

    @staticmethod
    def decrypt_file_content_from_session_pwdh(fname):
        with open(fname, 'rb') as fd:
            content = fd.read()
        return PasswordManager.decrypt_string_from_session_pwdh(content)

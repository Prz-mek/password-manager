from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
from Crypto.Hash import SHA256
from hashlib import sha256

def encrypt(key, plaintext):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plaintext, AES.block_size))
    iv = b64encode(cipher.iv).decode('utf-8')
    ciphertext = b64encode(ct_bytes).decode('utf-8')
    return ciphertext, iv


def decrypt(key, ciphertext, iv):
    iv = b64decode(iv)
    ct = b64decode(ciphertext)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ct), AES.block_size)
    return plaintext

def xor(a, b):
    tmp_list = [p^q for p, q in zip(a, b)]
    return bytes(tmp_list)


def prepare_password(password):
    while len(password) < 32:
        password += password
    return password[0:32].encode('utf-8')


def break_secret(secret):
    l1 = get_random_bytes(32)
    l2 = xor(l1, secret)
    return b64encode(l1), b64encode(l2)

def bind_secret(l1, l2):
    l1 = b64decode(l1)
    l2 = b64decode(l2)
    return xor(l1, l2)


if __name__ == '__main__':
    c = 'abc'
    p = prepare_password(c)
    print(p)
    l1, l2 = break_secret(p)
    print(l1, l2)
    print(bind_secret(l1, l2))
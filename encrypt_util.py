from cryptography.fernet import Fernet
import sys
import os

def encrypt_file(filename):
    if not os.path.isfile("./key"):
        get_key()
    keyfile = open("key", "rb")
    key = keyfile.read()
    keyfile.close()
    __encrypt_file(filename, key)


def decrypt_file(filename):
    keyfile = open("key", "rb")
    key = keyfile.read()
    keyfile.close()
    __decrypt_file(filename, key)

def __encrypt_file(filename, key):
    f = Fernet(key)

    plainfile = open(filename, "rb")
    plaintext = plainfile.read()
    plainfile.close()

    ciphertext = f.encrypt(plaintext)
    cipherfile = open(filename+".e", "wb+")
    cipherfile.write(ciphertext)
    cipherfile.close()


def __decrypt_file(filename, key):
    f = Fernet(key)

    cipherfile = open(filename, "rb")
    ciphertext = cipherfile.read()
    cipherfile.close()
    plaintext = f.decrypt(ciphertext)

    if filename.endswith(".e"):
        plain_filename = filename[:-2]
    else:
        plain_filename = "decrypted_file_"+filename

    plainfile = open(plain_filename, "wb+")
    plainfile.write(plaintext)
    plainfile.close()


def get_key():
    key = Fernet.generate_key()
    keyfile = open("key", "wb+")
    keyfile.write(key)
    keyfile.close()


def main():
    if sys.argv[1] == "encrypt":
        if not os.path.isfile("./key"):
            get_key()
        keyfile = open("key", "rb")
        key = keyfile.read()
        keyfile.close()
        __encrypt_file(sys.argv[2], key)

    elif sys.argv[1] == "decrypt":
        keyfile = open("key", "rb")
        key = keyfile.read()
        keyfile.close()
        __decrypt_file(sys.argv[2], key)


if __name__ == "__main__":
    main()


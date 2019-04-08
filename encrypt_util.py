from cryptography.fernet import Fernet
import sys
import os

def encrypt_file(folder, filename, key):

    f = Fernet(key)
    plainfile = open(folder+filename, "rb")
    plaintext = plainfile.read()
    plainfile.close()

    ciphertext = f.encrypt(plaintext)
    cipherfile = open(folder + ".encrypted/" + filename+ ".e", "wb+")
    cipherfile.write(ciphertext)
    cipherfile.close()


def decrypt_file(folder, filename, key):

    f = Fernet(key)
    cipherfile = open(folder + ".encrypted/" + filename, "rb")
    ciphertext = cipherfile.read()
    cipherfile.close()
    plaintext = f.decrypt(ciphertext)

    if filename.endswith(".e"):
        plain_filename = folder+filename[:-2]
    else:
        plain_filename = folder+"/decrypted_file_"+filename

    plainfile = open(plain_filename, "wb+")
    plainfile.write(plaintext)
    plainfile.close()


def create_key(write_path):
    key = Fernet.generate_key()
    keyfile = open("./secrets/"+write_path, "wb+")
    keyfile.write(key)
    keyfile.close()
    return key
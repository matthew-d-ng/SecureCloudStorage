from cryptography.fernet import Fernet


key = Fernet.generate_key()
f = Fernet(key)

plainfile = open(argv[1], "rb")
plaintext = plainfile.read()

ciphertext = f.encrypt(plaintext)
cipherfile = open("encrypt.bleh", "wb+")
cipherfile.write(ciphertext)
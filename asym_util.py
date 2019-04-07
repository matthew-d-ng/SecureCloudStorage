from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def new_priv_key():

  private_key = rsa.generate_private_key(
      public_exponent=65537,
      key_size=2048,
      backend=default_backend()
  )
  pem = private_key.private_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PrivateFormat.PKCS8,
      encryption_algorithm=serialization.NoEncryption()
  )
  keyfile = open("./secrets/priv_key.pem", "wb+")
  keyfile.write(pem)
  keyfile.close()


def set_public_key(private_key):
  
  public_key = private_key.public_key()
  pem = public_key.public_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PublicFormat.SubjectPublicKeyInfo
  )
  keyfile = open("./public/pub_key.pem", "wb+")
  keyfile.write(pem)
  keyfile.close()


def read_priv_key():

  with open("./secrets/priv_key.pem", "rb") as keyfile:
    private_key = serialization.load_pem_private_key(
        keyfile.read(),
        password=None,
        backend=default_backend()
    )
  return private_key


def read_pub_key():

  with open("./public/pub_key.pem" "rb") as keyfile:
    public_key = serialization.load_pem_public_key(
        keyfile.read(),
        backend=default_backend()
    )
  return public_key


def encrypt(key, file):
  pass


def decrypt(key, file):
  pass

import asym_util
import os

def user_data_exists():
  return os.path.isfile("secrets/priv_key.pem") \
        and os.path.isfile("public/pub_key.pem")


def create_user_data():

  asym_util.new_priv_key()
  private_key = asym_util.read_priv_key()
  asym_util.set_public_key(private_key)


def init():

  if user_data_exists():
    print("User data found, continuing")
    return True
  else:
    response = input("User data not found. Do you want to create a new public/private key pair? [Y/N]: ")

    if response == "Y":
      print("Creating a new private/public key pair")
      create_user_data()
      if user_data_exists():
        return True
      else:
        print("Failed to create user data, exiting...")
        return False

    elif response == "N":
      print("Not creating user data, exiting program...")
    else:
      print("Could not parse your response, please type 'Y' to create user data or 'N' to cancel.")
  return False


if __name__ == "__main__":
  init()
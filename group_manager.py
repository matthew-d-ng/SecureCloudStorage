import os
import pickle
import encrypt_util

KEY_PATH = "./secrets/keys.pickle"
GROUP_LOCAL_PATH = "local.pickle"
USER_PATH = "users.pickle"
DRIVE_PATH = "drive_folders.pickle"

def init_dict_data(filename):

  try:
    dict_file = open(filename, "rb")
  except FileNotFoundError:
    dict_file = open(filename, "bw+")

  try:
    dict_mem = pickle.load(dict_file)
  except EOFError:
    dict_mem = dict()

  dict_file.close()
  return dict_mem


def update_file(data, filename):

  pickle_file = open(filename, "wb")
  pickle.dump(data, pickle_file)
  pickle_file.close()


def create_group(group_id, local_folder, drive_folder):

  group_key = encrypt_util.create_key(local_folder)
  add_group(group_id, local_folder, drive_folder, group_key)


def add_group(group_id, local_folder, drive_folder, key):

  __keys__[group_id] = key
  __group_local__[group_id] = local_folder
  __group_drive__[group_id] = drive_folder

  update_file(__keys__, KEY_PATH)
  update_file(__group_local__, GROUP_LOCAL_PATH)
  update_file(__group_drive__, DRIVE_PATH)
  

def remove_group(group_id):

  del __keys__[group_id]
  del __group_local__[group_id]
  update_file(__keys__, KEY_PATH)
  update_file(__group_local__, GROUP_LOCAL_PATH)


def update_group_key(group_id, key):

  __keys__[group_id] = key
  update_file(__keys__, KEY_PATH)


def get_group_key(group_id):

  return __keys__[group_id]


def get_group_name(group_id):

  return __group_local__[group_id]


def get_group_drive(group_id):

  return __group_drive__[group_id]


def add_user(group_id, user):
  
  if not group_id in __users__:
    __users__[group_id] = list()
  elif user in __users__[group_id]:
    return

  __users__[group_id].append(user)
  update_file(__users__, USER_PATH)
  # send group key to user


def remove_user(group_id, user):

  while user in __users__[group_id]:
    __users__[group_id].remove(user)
  update_file(__users__, USER_PATH)

  reencrypt_drive(group_id)
  new_key = get_group_key(group_id)
  for user in __users__[group_id]:
    send_key(user, new_key)


def reencrypt_drive(group_id):

  # for every file in the drive, 
  # decrypt it with the old key
  # and encrypt it with the new one
  pass


def send_key(user, new_key):

  # encrypt the symmetric key with users public key and send it on
  pass


def validate_key(group_id):

  our_key = get_group_key(group_id)
  # check version on drive, decrypt with our priv key
  # if they're the same all is good
  # else get the new key and update our values
  pass


def get_groups():

  return list(__group_drive__.keys())


def signin_to_group(group_id):

  validate_key(group_id)


__keys__ = init_dict_data(KEY_PATH)
__group_local__ = init_dict_data(GROUP_LOCAL_PATH)
__users__ = init_dict_data(USER_PATH)
__group_drive__ = init_dict_data(DRIVE_PATH)
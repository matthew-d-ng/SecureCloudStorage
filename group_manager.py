import os
import pickle
import encrypt_util
import asym_util

KEY_PATH = "./secrets/keys.pickle"
GROUP_LOCAL_PATH = "local.pickle"
USER_PATH = "users.pickle"
DRIVE_PATH = "drive_folders.pickle"
ADMIN_PATH = "admin.pickle"
METADATA_PATH = "metadata.pickle"
PUBLIC_PATH = "./public/user_keys.pickle"

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


def init_list_data(filename):

  try:
    list_file = open(filename, "rb")
  except FileNotFoundError:
    list_file = open(filename, "bw+")

  try:
    list_mem = pickle.load(list_file)
  except EOFError:
    list_mem = list()

  list_file.close()
  return list_mem


def update_file(data, filename):

  pickle_file = open(filename, "wb")
  pickle.dump(data, pickle_file)
  pickle_file.close()


def create_group(group_id, local_folder, drive_folder, metadata_folder):

  if group_id not in get_groups():
    __admin_groups__.append(group_id)
    update_file(__admin_groups__, ADMIN_PATH)
    group_key = encrypt_util.create_key(local_folder)
    __users__[group_id] = list()
    update_file(__users__, USER_PATH)
    add_group(group_id, local_folder, drive_folder, metadata_folder, group_key)
  else:
    print("Group ID already exists!")


def add_group(group_id, local_folder, drive_folder, metadata_folder, key):

  __keys__[group_id] = key
  __group_local__[group_id] = local_folder
  __group_drive__[group_id] = drive_folder
  __metadata__[drive_folder] = metadata_folder

  update_file(__keys__, KEY_PATH)
  update_file(__group_local__, GROUP_LOCAL_PATH)
  update_file(__group_drive__, DRIVE_PATH)
  update_file(__metadata__, METADATA_PATH)


def remove_group(group_id):

  os.remove("./secrets/"+get_group_name(group_id))
  while group_id in __admin_groups__:
    __admin_groups__.remove(group_id)

  del __keys__[group_id]
  del __group_local__[group_id]
  del __metadata__[get_group_drive(group_id)]

  update_file(__keys__, KEY_PATH)
  update_file(__group_local__, GROUP_LOCAL_PATH)
  update_file(__metadata__, METADATA_PATH)


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
  # __public_keys__[user] = public_key
  update_file(__users__, USER_PATH)
  # update_file(__public_keys__, PUBLIC_PATH)
  # send_key(user, get_group_key(group_id))


def remove_user(group_id, user):

  while user in __users__[group_id]:
    __users__[group_id].remove(user)
  update_file(__users__, USER_PATH)


def get_user_public_key(user):

  return __public_keys__[user]


def get_group_metadata_folder(group_id):

  group_drive = get_group_drive(group_id)
  return __metadata__[group_drive]


def get_users(group_id):

  return list(__users__[group_id])


def get_groups():

  return list(__group_drive__.keys())


def is_admin(group_id):

  return group_id in __admin_groups__


__admin_groups__ = init_list_data(ADMIN_PATH)
__metadata__ = init_dict_data(METADATA_PATH)
__keys__ = init_dict_data(KEY_PATH)
__group_local__ = init_dict_data(GROUP_LOCAL_PATH)
__users__ = init_dict_data(USER_PATH)
__public_keys__ = init_dict_data(PUBLIC_PATH)
__group_drive__ = init_dict_data(DRIVE_PATH)

# acting under the presumption that these values
# exist on a publically available secure server

__public_keys__["ngm1"] = asym_util.read_pub_key("./public/pub_key.pem")
__public_keys__["matthew.d.ng"] = asym_util.read_pub_key("./public/user_keys/pub_key.pem")

""" Matthew Ng ngm1@tcd.ie 16323205
    Telecomms Assignment 2: Secure the Cloud
"""

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from encrypt_util import encrypt_file
from encrypt_util import decrypt_file
import os
import json
import asym_manager
import asym_util
import group_manager
import encrypt_util

FOLDER = "application/vnd.google-apps.folder"

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

def ls_folders(folder_id):

    folder_list = drive.ListFile(
            {'q': "'%s' in parents and trashed=false and mimeType = '%s'" \
                % (folder_id, FOLDER)}).GetList()
    print("FOLDERS:")
    for i in range(len(folder_list)):
        file1 = folder_list[i]
        print(" %d: title: %s" % (i, file1["title"]))

    return folder_list


def ls_files(folder_id):

    file_list = drive.ListFile(
            {'q': "'%s' in parents and trashed=false and mimeType != '%s'" \
                % (folder_id, FOLDER)}
            ).GetList()
    print("FILES: ")
    for i in range(len(file_list)):
        file1 = file_list[i]
        print(" %d: title: %s" % (i, file1["title"]))

    return file_list


def ls_directory(folder_id):

    folder_list = ls_folders(folder_id)
    file_list = ls_files(folder_id)

    return (folder_list, file_list)


def validate_key(username, group_id):

    # check our key and drive key
    metadata = group_manager.get_group_metadata_folder(group_id)
    drive_version = get_key(username, metadata)
    our_version = group_manager.get_group_key(group_id)

    if drive_version != our_version:
        print("Drive key has changed, updating our value...")
        group_manager.update_group_key(group_id, drive_version)


def signin_to_group(username, group_id):

  if not group_manager.is_admin(group_id):
    validate_key(username, group_id)


def user_create_group():

    name = input("Enter group name: ")
    group_id = input("Enter a group id: ")

    group_folder = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": "root"}]})
    group_folder["mimeType"] = FOLDER
    group_folder["title"] = name
    group_folder.Upload()

    metadata = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": group_folder["id"]}]})
    metadata["title"] = ".metadata"
    metadata["mimeType"] = FOLDER
    metadata.Upload()

    local_folder = "./secure_files/{}".format(name)
    os.mkdir(local_folder)
    os.mkdir(local_folder+"/.encrypted")

    group_manager.create_group( group_id, name, group_folder["id"], metadata["id"])

    upload_group_key(group_id)

    return group_id


def update_group_key(group_id):

    if group_manager.is_admin(group_id):

        metadata_folder = group_manager.get_group_metadata_folder(group_id)
        group_key = group_manager.get_group_key(group_id)
        
        for user in group_manager.get_users(group_id):
            key_file = drive.ListFile(
                {'q': "'%s' in parents and trashed=false and title = '%s'" \
                    % (metadata_folder["id"], user)}).GetList()[0]

            pub_key = group_manager.get_user_public_key(user)
            encrypted_key = asym_util.encrypt(pub_key, group_key)

            local_key = open("temp_local_key", "wb+")
            local_key.write(encrypted_key)
            local_key.close()

            key_file.SetContentFile("temp_local_key")
            key_file["title"] = user
            key_file.Upload()
    else:
        print("You are not the administrator!")


def upload_group_key(group_id):

    if group_manager.is_admin(group_id):
        metadata_folder = group_manager.get_group_metadata_folder(group_id)
        group_key = group_manager.get_group_key(group_id)

        for user in group_manager.get_users(group_id):
            pub_key = group_manager.get_user_public_key(user)
            encrypted_key = asym_util.encrypt(pub_key, group_key)

            local_key = open("temp_local_key", "wb+")
            local_key.write(encrypted_key)
            local_key.close()

            key_file = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": metadata_folder}]})
            key_file["title"] = user
            key_file.SetContentFile("temp_local_key")
            key_file.Upload()
    else:
        print("You are not the administrator!")


def get_key(username, metadata):

    key_file = drive.ListFile(
        {'q': "'%s' in parents and trashed=false and title = '%s'" \
            % (metadata, username)}).GetList()[0]

    key_file.GetContentFile("temp_local_key")
    encrypted_file = open("temp_local_key", "rb")
    encrypted_key = encrypted_file.read()

    priv_key = asym_util.read_priv_key()
    group_key = asym_util.decrypt(priv_key, encrypted_key)
    return group_key


def user_join_group(username):

    # folder_list = ls_folders("root")
    folder_list = drive.ListFile(
            {'q': "sharedWithMe = True"}).GetList()
    print("FOLDERS:")
    for i in range(len(folder_list)):
        file1 = folder_list[i]
        print(" %d: title: %s" % (i, file1["title"]))

    index = int(input("Select Folder number: "))
    folder = folder_list[index]
    metadata = drive.ListFile(
            {'q': "'%s' in parents and trashed=false and title = '%s'" \
                % (folder["id"], ".metadata")}).GetList()[0]

    group_id = input("Assign a group id: ")
    key = get_key(username, metadata["id"])

    local_folder = "./secure_files/{}".format(folder["title"])
    os.mkdir(local_folder)
    os.mkdir(local_folder+"/.encrypted")

    group_manager.add_group(group_id, folder["title"], folder["id"], metadata["id"], key)

    return group_id


def select_group(username):

    group_list = group_manager.get_groups()

    if len(group_list) > 0:
        print("Groups: ")
        for i in range(len(group_list)):
            group_name = group_manager.get_group_name(group_list[i])
            print("  {}: {}".format(i, group_name))

        print("You are in {} groups".format(len(group_list)))
        user_cmd = input("Sign in, join a group or create one [signin/join/create]: ")

        if user_cmd == "signin":
            index = int(input("Input group number: "))
            group_id = group_list[index]
        elif user_cmd == "create":
            group_id = user_create_group()
        elif user_cmd == "join":
            group_id = user_join_group(username)
        else:
            print("Command not recognised")
            return

    else:
        user_cmd = input("You are not in any groups, do you want to create or join one? [create/join]")
        if user_cmd == "create":
            group_id = user_create_group()
        elif user_cmd == "join":
            group_id = user_join_group(username)
        else:
            print("Command not recognised, type either create or join")
            return

    signin_to_group(username, group_id)
    print("Signed in to group ", group_manager.get_group_name(group_id))
    return group_id


def reencrypt_drive(group_id):

    local_folder = "secure_files/" + group_manager.get_group_name(group_id) + "/"
    drive_folder = group_manager.get_group_drive(group_id)
    file_list = ls_files(drive_folder)

    old_key = group_manager.get_group_key(group_id)
    new_key = encrypt_util.create_key(group_manager.get_group_name(group_id))
    group_manager.update_group_key(group_id, new_key)
    print(old_key)
    print(new_key)

    for file1 in file_list:
        file1.GetContentFile(local_folder+".encrypted/"+file1["title"]+".e")
        decrypt_file(local_folder, file1["title"]+".e", old_key)

        encrypt_file(local_folder, file1["title"], new_key)
        file1.SetContentFile(local_folder + ".encrypted/" + file1["title"] + ".e")
        file1.Upload()

    update_group_key(group_id)


def main():

    # make sure user details are good to go
    asym_manager.init()
    username = input("Username: ")
    # user selects group to use
    group_id = select_group(username)
    folder_id = group_manager.get_group_drive(group_id)
    root = folder_id
    local_folder = "secure_files/" + group_manager.get_group_name(group_id) + "/"

    current_dir = drive.CreateFile({"id": folder_id})

    while(True):

        dir_list = ls_directory(folder_id)
        folder_list = dir_list[0]
        file_list = dir_list[1]

        user_cmd = input("?> ").split(" ")

        if user_cmd[0] == "cd":
            next_dir = user_cmd[1]
            if next_dir == "..":
                if folder_id != root:
                    current_dir = drive.CreateFile({'id': current_dir["parents"][0]["id"]})
                else:
                    print("No parent")
            else:
                current_dir = folder_list[int(next_dir)]
            folder_id = current_dir["id"]

        elif user_cmd[0] == "dl":
            file_index = int(user_cmd[1])
            dl_file = file_list[file_index]
            dl_file.GetContentFile(local_folder+".encrypted/"+dl_file["title"]+".e")

            key = group_manager.get_group_key(group_id)
            decrypt_file(local_folder, dl_file["title"]+".e", key)

        elif user_cmd[0] == "up":
            filename = user_cmd[1]
            up_file = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": folder_id}]})

            key = group_manager.get_group_key(group_id)
            encrypt_file(local_folder, filename, key)

            up_file.SetContentFile(local_folder + ".encrypted/" + filename + ".e")
            up_file["title"] = filename
            up_file.Upload()

        elif user_cmd[0] == "add":
            new_user = user_cmd[1]
            group_manager.add_user(group_id, new_user)
            upload_group_key(group_id)

        elif user_cmd[0] == "kick":
            kicked_user = user_cmd[1]
            group_manager.remove_user(group_id, kicked_user)
            reencrypt_drive(group_id)


if __name__ == '__main__':
    main()

""" Matthew Ng ngm1@tcd.ie 16323205
    Telecomms Assignment 2: Secure the Cloud
"""

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from encrypt_util import encrypt_file
from encrypt_util import decrypt_file
import os
import asym_manager
import group_manager

FOLDER = "application/vnd.google-apps.folder"

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

def ls_directory(folder_id):

    folder_list = drive.ListFile({'q': "'%s' in parents and trashed=false and mimeType = '%s'" % (folder_id, FOLDER)}).GetList()
    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false and mimeType != '%s'" % (folder_id, FOLDER)}).GetList()

    print("FOLDERS:")
    for i in range(len(folder_list)):
        file1 = folder_list[i]
        print(" %d: title: %s" % (i, file1["title"]))

    print("FILES: ")
    for i in range(len(file_list)):
        file1 = file_list[i]
        print(" %d: title: %s" % (i, file1["title"]))

    return (folder_list, file_list)


def user_create_group():

    name = input("Enter group name: ")
    group_id = input("Enter a group id: ")

    group_folder = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": "root"}]})
    group_folder["mimeType"] = FOLDER
    group_folder["title"] = name
    group_folder.Upload()
    local_folder = "./secure_files/{}".format(name)
    os.mkdir(local_folder)
    os.mkdir(local_folder+"/.encrypted")

    group_manager.create_group( group_id, name, group_folder["id"] )
    return group_id


def user_join_group():

    # select folder where group is (already invited on google drive)
    # check metadata
    return "root"


def select_group():

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
            group_id = user_join_group()
        else:
            print("Command not recognised")
            return

    else:
        user_cmd = input("You are not in any groups, do you want to create or join one? [create/join]")
        if user_cmd == "create":
            group_id = user_create_group()
        elif user_cmd == "join":
            group_id = user_join_group()
        else:
            print("Command not recognised, type either create or join")
            return

    group_manager.signin_to_group(group_id)
    print("Signed in to group ", group_manager.get_group_name(group_id))
    return group_id


def main():
    """ WILL PROBABLY PUT A LOT OF THIS UNDER SEPARATE FUNCTION """

    # make sure user details are good to go
    asym_manager.init()

    # user selects group to use
    group_id = select_group()
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


if __name__ == '__main__':
    main()

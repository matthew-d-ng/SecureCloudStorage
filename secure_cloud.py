
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

def user_create_group():

    name = input("Enter group name: ")
    group_folder = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": "root"}]})
    group_folder["mimeType"] = FOLDER
    # choose name to use, autogenerate ID and drive folder
    # maybe return details in an object
    # make group dicts store objects?
    pass


def user_join_group():

    # select folder where group is (already invited on google drive)
    # check metadata
    pass


def select_group():

    group_list = group_manager.get_groups()

    if len(group_list) > 0:
        print("Groups: ")
        for i in range(len(group_list)):
            group_name = group_manager.get_group_name(group_list[i])
            print("  {}: {}".format(i, group_name))

        print("You are in {} groups".format(len(group_list))
        cmd = input("Sign in to an existing group, \
                    create a new group, \
                    or join another one [signin/create/join]")

        if cmd == "signin":
            index = int(input("Input group number: "))
            group_id = group_list[index]
        elif cmd == "create":
            user_create_group()
        elif cmd == "join":
            user_join_group()
        else:
            print("Command not recognised")

    else:
        cmd = input("You are not in any groups, do you want to create or join one? [create/join]")
        if cmd == "create":
            user_create_group()
        elif cmd == "join":
            user_join_group()
        else:
            print("Command not recognised, type either create or join")

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
    local_folder = "secure_files/" + group_manager.get_group_name(group_id)

    current_dir = drive.CreateFile({"id": folder_id})

    while(True):
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
            dl_file.GetContentFile(dl_file["title"])
            decrypt_file(dl_file["title"])
            #os.remove(local_folder + dl_file["title"])

        elif user_cmd[0] == "up":
            filename = user_cmd[1]
            up_file = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": folder_id}]})
            encrypt_file(local_folder + filename)
            up_file.SetContentFile(local_folder + filename + ".e")
            up_file["name"] = filename
            up_file.Upload()
            #os.remove(LOCAL_FOLDER + filename+".e")


if __name__ == '__main__':
    main()

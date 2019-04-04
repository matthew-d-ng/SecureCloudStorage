
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from encrypt_util import encrypt_file
from encrypt_util import decrypt_file
import os

FOLDER = "application/vnd.google-apps.folder"
LOCAL_FOLDER = "secure_files/"

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)


def main():
    folder_id = "root"
    current_dir = drive.CreateFile({"id": folder_id})

    while(True):
        folder_list = drive.ListFile({'q': "'%s' in parents and trashed=false and mimeType = '%s'" % (folder_id, FOLDER)}).GetList()
        file_list = drive.ListFile({'q': "'%s' in parents and trashed=false and mimeType != '%s'" % (folder_id, FOLDER)}).GetList()

        print("FOLDERS:")
        for i in range(len(folder_list)):
            file1 = folder_list[i]
            print(" %d: title: %s, id: %s" % (i, file1["title"], file1["id"]))

        print("FILES: ")
        for i in range(len(file_list)):
            file1 = file_list[i]
            print(" %d: title: %s, id: %s" % (i, file1["title"], file1["id"]))


        user_cmd = input("?> ").split(" ")

        if user_cmd[0] == "cd":
            next_dir = user_cmd[1]
            if next_dir == "..":
                if folder_id is not "root":
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
            #os.remove(LOCAL_FOLDER + dl_file["title"])

        elif user_cmd[0] == "up":
            filename = user_cmd[1]
            up_file = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": folder_id}]})
            encrypt_file(LOCAL_FOLDER + filename)
            up_file.SetContentFile(LOCAL_FOLDER + filename + ".e")
            up_file["name"] = filename
            up_file.Upload()
            #os.remove(LOCAL_FOLDER + filename+".e")


if __name__ == '__main__':
    main()

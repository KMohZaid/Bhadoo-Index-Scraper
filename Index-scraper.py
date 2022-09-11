import requests
import base64
import json
import urllib
next_page = False
next_page_token = ""

index_url_list = {
    "folders": {},  # folder might have folders so dictionary
    "files": []  # file cant contain other file and folder so list
}  # each file have 2 item name and url
# files = {name,url}
# folders = {folder1:{folders,files},...}


def authorization_token(username, password):
    user_pass = f"{username}:{password}"
    token = "Basic " + base64.b64encode(user_pass.encode()).decode()
    return token


def decrypt(string):
    return base64.b64decode(string[::-1][24:-20]).decode('utf-8')


def process_page(payload_input, url, current_dict, username, password):
    global next_page
    global next_page_token

    url = url + "/" if url[-1] != '/' else url

    try:
        headers = {"authorization": authorization_token(username, password)}
    except:
        return "username/password combination is wrong"

    encrypted_response = requests.post(
        url, data=payload_input, headers=headers)
    if encrypted_response.status_code == 401:
        return "username/password combination is wrong"

    try:
        decrypted_response = json.loads(decrypt(encrypted_response.text))
    except:
        return "something went wrong. check index link/username/password field again"

    page_token = decrypted_response["nextPageToken"]
    if page_token == None:
        next_page = False
    else:
        next_page = True
        next_page_token = page_token

    if list(decrypted_response.get("data").keys())[0] == "error":
        pass
    else:
        length = len(decrypted_response["data"]["files"])
        for i, _ in enumerate(range(length)):
            type = decrypted_response["data"]["files"][i]["mimeType"]
            name = decrypted_response["data"]["files"][i]["name"]
            link = url + urllib.parse.quote(name)
            if type == "application/vnd.google-apps.folder":  # if folder
                link += "/"
                current_dict["folders"][name] = {
                    "folders": {},
                    "files": []
                }
                list_index_files(
                    link, current_dict["folders"][name], username, password)
            else:  # else it is file
                current_dict["files"].append({"name": name, "url": link})


def list_index_files(url, current_dict, username="none", password="none"):
    x = 0
    payload = {"page_token": next_page_token, "page_index": x}
    process_page(payload, url, current_dict, username, password, )
    while next_page == True:
        payload = {"page_token": next_page_token, "page_index": x}
        print(process_page(payload, url, username, password))
        x += 1


index_link = ""
username = ""  # optional
password = ""  # optional

list_index_files(url=index_link, current_dict=index_url_list,
                 username=username, password=password)
print(index_url_list)
# better then print :
open("output.py", "w",
     encoding="utf-8").write(f"index_url_list={json.dumps(index_url_list,indent=4)}")

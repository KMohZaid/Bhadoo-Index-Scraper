import requests
import base64
import json
import urllib


class IndexScrapper:
    next_page = False
    next_page_token = ""

    index_url_list = {
        "folders": {},  # folder might have folders so dictionary
        "files": []  # file cant contain other file and folder so list
    }  # each file have 2 item name and url
    # files = {name,url}
    # folders = {folder1:{folders,files},...}

    def __init__(self, index_link, username="none", password="none"):
        self.index_link = index_link
        self.username = username
        self.password = password
        self.auth_token = self.authorization_token()

    def authorization_token(self):
        user_pass = f"{self.username}:{self.password}"
        token = "Basic " + base64.b64encode(user_pass.encode()).decode()
        return token

    def decrypt(self, string):
        return base64.b64decode(string[::-1][24:-20]).decode('utf-8')

    def process_page(self, payload_input, current_dict, url):
        url = url + "/" if url[-1] != '/' else url
        headers = {"authorization": self.auth_token}

        encrypted_response = requests.post(
            url, data=payload_input, headers=headers)
        if encrypted_response.status_code == 401:
            return print("username/password combination is wrong")
        if encrypted_response.status_code >= 400:  # 2xx have no error so
            print(
                f"ERROR {encrypted_response.status_code} = {encrypted_response.reason}")
            raise Exception(
                f"ERROR {encrypted_response.status_code} = {encrypted_response.reason}", {"details": {"url": url, "currently_listed": self.index_url_list}})
        try:
            decrypted_response = json.loads(
                self.decrypt(encrypted_response.text))
        except:
            return print("something went wrong. check index link/username/password field again")

        page_token = decrypted_response["nextPageToken"]
        if page_token == None:
            self.next_page = False
        else:
            self.next_page = True
            self.next_page_token = page_token

        if list(decrypted_response.get("data").keys())[0] == "error":
            pass
        else:
            length = len(decrypted_response["data"]["files"])
            for i, _ in enumerate(range(length)):
                type = decrypted_response["data"]["files"][i]["mimeType"]
                name = decrypted_response["data"]["files"][i]["name"]
                link = self.index_link + urllib.parse.quote(name)
                if type == "application/vnd.google-apps.folder":  # if folder
                    link += "/"
                    current_dict["folders"][name] = {
                        "folders": {},
                        "files": []
                    }
                    self.list_index_files(current_dict["folders"][name], link)
                else:  # else it is file
                    current_dict["files"].append({"name": name, "url": link})

    def list_index_files(self, current_dict=None, url=None):
        try:
            if not current_dict:
                current_dict = self.index_url_list
            if not url:
                url = self.index_link
            x = 0
            payload = {"page_token": self.next_page_token, "page_index": x}
            self.process_page(payload, current_dict, url)
            while self.next_page == True:
                payload = {"page_token": self.next_page_token, "page_index": x}
                self.process_page(payload, current_dict, url)
                x += 1
        except Exception as e:
            pass


index_link = ""
username = ""
password = ""

# username and password only if your index is protected by username and password
scrapper = IndexScrapper(index_link, username, password)
scrapper.list_index_files()
print(scrapper.index_url_list)
# better then print :
open("output.py", "w",
     encoding="utf-8").write(f"index_url_list={json.dumps(scrapper.index_url_list,indent=4)}")

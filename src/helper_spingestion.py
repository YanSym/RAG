from pathlib import Path
import requests
import msal
import re
import os


class SharePointDownloader:
    """Class to download files from SharePoint using Microsoft Graph API."""

    GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(
        self,
        tenant_id,
        client_id,
        client_secret,
        site_url,
        library,
        download_folder,
        flag_debug,
    ):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.site_url = site_url
        self.library = library
        self.download_folder = download_folder
        self.flag_debug = flag_debug
        self.token = self.get_access_token()
        self.site_id = self.get_site_id()

    def sanitize_path(self, name):
        return re.sub(r'[<>:"/\\|?*]', "_", name)

    def get_access_token(self):
        """Get an access token for Microsoft Graph API."""
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        scope = ["https://graph.microsoft.com/.default"]

        app = msal.ConfidentialClientApplication(
            self.client_id, authority=authority, client_credential=self.client_secret
        )
        result = app.acquire_token_for_client(scopes=scope)
        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception(f"Token error: {result.get('error_description')}")

    def get_site_id(self):
        """Get the site ID from the SharePoint site URL."""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(self.site_url, headers=headers)
        response.raise_for_status()
        site_id = response.json()["id"]
        if self.flag_debug:
            print(f"Site ID: {site_id}")
        return site_id

    def get_drive_id_by_name(self, drive_name):
        """Get the drive ID by its name."""
        url = f"{self.GRAPH_BASE_URL}/sites/{self.site_id}/drives"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        drives = response.json()["value"]

        for drive in drives:
            if drive["name"].strip().lower() == drive_name.strip().lower():
                if self.flag_debug:
                    print(f"Drive '{drive_name}' com ID: {drive['id']}")
                return drive["id"]

        raise ValueError(f"Biblioteca '{drive_name}' não foi encontrada.")

    def download_files_recursive(self, folder_path=""):
        """Recursively download all files from the given SharePoint drive."""
        drive_id = self.get_drive_id_by_name(self.library)

        if folder_path == "":
            url = f"{self.GRAPH_BASE_URL}/drives/{drive_id}/root/children"
        else:
            url = (
                f"{self.GRAPH_BASE_URL}/drives/{drive_id}/root:/{folder_path}:/children"
            )

        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            if self.flag_debug:
                print(f"Erro listando diretorio {folder_path}: {e}")
            return

        # load response
        items = response.json()["value"]

        # iterate items
        for item in items:
            item_name = item["name"]
            item_path = os.path.join(folder_path, item_name)

            if "folder" in item:
                # Recurse into subfolder
                try:
                    self.download_files_recursive(item_path)
                except Exception:
                    continue

            elif "file" in item:
                # Download file
                try:
                    # Download file
                    download_url = item["@microsoft.graph.downloadUrl"]
                    filename = self.sanitize_path(item["name"])
                    local_path = Path(self.download_folder) / filename
                    file_data = requests.get(download_url)

                    # save file
                    with open(local_path, "wb") as f:
                        f.write(file_data.content)

                    if self.flag_debug:
                        print(f"Downloaded: {item_path}")
                except Exception as e:
                    if self.flag_debug:
                        print("Erro:", e)

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import json

# Load configuration from config.json
config_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "config.json"
)

current_directory = os.getcwd()
credentials_path = os.path.join(current_directory, "credentials.json")

with open(config_path, "r") as config_file:
    config = json.load(config_file)

FOLDER_ID = config["google_drive_folder_id"]
SERVICE_ACCOUNT_FILE = credentials_path

# Initialize the Google Drive API using the service account credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)


class GDriveHandler:
    def __init__(self, pc_folder_path):
        self.pc_folder_path = pc_folder_path

    def get_all_folders(self):
        results = (
            drive_service.files()
            .list(
                q=f"'{FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder'",
                fields="files(id, name)",
                orderBy="createdTime",
            )
            .execute()
        )

        folder_files = results.get("files", [])
        return folder_files

    def get_all_media_files(self, account_folder_id):
        results = (
            drive_service.files()
            .list(
                q=f"'{account_folder_id}' in parents and (mimeType contains 'video/' or mimeType contains 'image/')",
                fields="files(id, name, mimeType)",
                orderBy="createdTime",
            )
            .execute()
        )

        media_files = results.get("files", [])

        # Add a 'media_type' field to each file in the results
        for file_info in media_files:
            mime_type = file_info.get("mimeType", "")
            if "video/" in mime_type:
                file_info["media_type"] = "video"
            elif "image/" in mime_type:
                file_info["media_type"] = "image"
            else:
                file_info["media_type"] = "unknown"

        return media_files

    def download_files(self, video_file):
        # Create PC folder if not exists
        if not os.path.exists(self.pc_folder_path):
            os.makedirs(self.pc_folder_path)

        download_path = self.pc_folder_path

        if video_file:
            file_id = video_file["id"]
            file_name = video_file["name"]

            # Construct the complete download path including the file name
            download_path = os.path.join(download_path, file_name)

            # Download the video file
            request = drive_service.files().get_media(fileId=file_id)
            with open(download_path, "wb") as file:
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}%")

            print(f"Downloaded '{file_name}' to {os.path.abspath(download_path)}")
            return download_path
        else:
            print("Video file not found.")
            return 0

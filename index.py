import time
import uiautomator2 as u2
from gdrive_handler import GDriveHandler
from file_uploader import FileUploader


def main():
    d = u2.connect()

    pc_folder_path = "./videos"

    gdrive_handler = GDriveHandler(pc_folder_path)

    video_files = gdrive_handler.get_all_videos()

    for video in video_files:
        pc_vid_path = gdrive_handler.download_files(video)
        file_handler = FileUploader(pc_vid_path)

        android_vid_path = file_handler.transfer_file_to_device(d)
        file_handler.upload_reel(d, android_vid_path)

        time.sleep(1500)


main()

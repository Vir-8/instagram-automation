from gdrive_handler import GDriveHandler


def main():
    drive_folder_url = "https://drive.google.com/your_drive_folder_url"
    pc_folder_path = "./videos"

    file_handler = GDriveHandler(drive_folder_url, pc_folder_path)
    video_files = file_handler.get_all_videos()

    for video in video_files:
        file_handler.download_files(video)


main()

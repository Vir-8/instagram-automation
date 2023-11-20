import time
import uiautomator2 as u2
from uiautomator2 import Device
import random
import adbutils
from gdrive_handler import GDriveHandler
from file_uploader import FileUploader
from growth_handler import GrowthHandler
from account_handler import AccountHandler
import concurrent.futures
import json

RANDOM_ACTIVITY_TIME = 60

resource_ids = {"home_button": "com.instagram.android:id/feed_tab"}

# Load configuration from config.json
with open("account_config.json", "r") as config_file:
    account_config = json.load(config_file)


def random_activity(d: Device):
    print(f"Performing random activity on device: {d.serial}")

    activity_handler = GrowthHandler(d)
    # Click on home in case home isn't open
    d(resourceId=resource_ids["home_button"]).click()
    time.sleep(2)

    # Perform random activity for a set time, scrolling or liking at random intervals
    total_duration = RANDOM_ACTIVITY_TIME

    scroll_chances = 0.3  # 70%
    like_chances = 0.3  # 30%
    comment_chances = 0.1  # 10%

    # Start time of the loop
    start_time = time.time()

    # Main loop
    while time.time() - start_time < total_duration:
        # Generate random time interval and number
        interval = random.uniform(3, 7)
        random_number = random.random()
        print(f"Random number is {random_number}")

        if random_number > scroll_chances:
            # Swipe the screen from bottom to top
            print("Scrolling")
            activity_handler.scroll(0.3)
        elif random_number < like_chances:
            print("Liking")
            activity_handler.like_post()
            if random_number < comment_chances:
                print("Commenting")
                activity_handler.comment_on_post()
                activity_handler.scroll(0.3)

        time.sleep(interval)

    time.sleep(2)


def account_growth_handler(device):
    d = u2.connect(device)
    account_handler = AccountHandler(d)
    growth_handler = GrowthHandler(d)

    accounts = account_handler.get_all_accounts()

    for account in accounts:
        account_handler.switch_account(account)
        growth_handler.follow_accounts()
        growth_handler.promote_accounts()
        time.sleep(8)


def content_upload_handler(device):
    d = u2.connect(device)
    d.dump_hierarchy()  # As ADB can cause issues otherwise
    pc_folder_path = "./videos"

    gdrive_handler = GDriveHandler(pc_folder_path)
    account_handler = AccountHandler(d)

    accounts = [
        (account, folder_id)
        for account, folder_id in account_config["devices"].get(device, {}).items()
        if folder_id != "N/A"
    ]

    videos = {account: [] for account, folder_id in accounts}

    for account, folder_id in accounts:
        videos_on_account = gdrive_handler.get_all_videos(folder_id)
        videos[account] = videos_on_account

    while any(videos.values()):
        for account, folder_id in accounts:
            video_list = videos[account]
            account_handler.switch_account(account)

            if video_list:
                current_video = video_list[0]
                print(
                    f"Downloading {current_video['name']} for account: {account} on device: {device}."
                )
                pc_vid_path = gdrive_handler.download_files(current_video)

                file_handler = FileUploader(pc_vid_path)
                android_vid_path = file_handler.transfer_file_to_device(d)
                file_handler.upload_reel(d, android_vid_path)

                print(
                    f"Video '{current_video['name']}' uploaded for account '{account}'."
                )

                # Remove the uploaded video from the account's video list
                videos[account] = video_list[1:]

                random_activity(d)
                time.sleep(1500)


def main():
    connected_devices = [device.serial for device in adbutils.adb.device_list()]
    choice = input("1. Upload videos\n2. Grow accounts\nEnter your choice: ")

    if choice == "1":
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(connected_devices)
        ) as executor:
            executor.map(content_upload_handler, connected_devices)
    elif choice == "2":
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(connected_devices)
        ) as executor:
            # Pass the instances as arguments to the threaded function
            executor.map(account_growth_handler, connected_devices)
    else:
        print("Error! Invalid choice, please try again!")


main()

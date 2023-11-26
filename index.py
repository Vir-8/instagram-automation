import time
import uiautomator2 as u2
from uiautomator2 import Device
import random
import adbutils
from classes.gdrive_handler import GDriveHandler
from classes.file_uploader import FileUploader
from classes.growth_handler import GrowthHandler
from classes.account_handler import AccountHandler
import concurrent.futures
import json
import os

resource_ids = {
    "home_button": "com.instagram.android:id/feed_tab",
    "explore_button": "com.instagram.android:id/search_tab",
}

# Load configuration from config.json
with open("account_config.json", "r") as config_file:
    account_config = json.load(config_file)

with open("config.json", "r") as file:
    config_data = json.load(file)

RANDOM_ACTIVITY_TIME = config_data["random_activity_time_in_mins"]


def random_activity(d: Device, total_duration):
    # Perform random activity for a set time, scrolling or liking at random intervals
    print(f"Performing random activity on device: {d.serial}")

    activity_handler = GrowthHandler(d)
    time.sleep(4)

    # Click on home in case home isn't open
    d(resourceId=resource_ids["explore_button"]).click()
    time.sleep(2)

    # Click on a post on the explore page

    scroll_chances = 0.3  # 70%
    like_chances = 0.3  # 30%
    comment_chances = 0.1  # 10%

    random_combinations = []
    num_of_posts = 7

    for row in range(1, 4):
        for col in range(1, 4):
            if not (row in [1, 2] and col == 3):
                random_combinations.append(
                    (f"row {row}, column {col}", f"column {col}, row {row}")
                )

    # Fetch all elements with the description attribute using XPath
    elements_with_description = d.xpath("//*[@content-desc]").all()
    start_time = time.time()

    time_per_post = total_duration / num_of_posts

    while time.time() - start_time < total_duration:
        for desc1, desc2 in random_combinations:
            # Find the post and click
            for element in elements_with_description:
                if (
                    desc1.lower() in element.info["contentDescription"].lower()
                    or desc2.lower() in element.info["contentDescription"].lower()
                ):
                    element.click()

                    # Perform random activity on selected post
                    clicked_time = time.time()
                    while time.time() - clicked_time < time_per_post:
                        # Generate random time interval and number
                        interval = random.uniform(1, 5)
                        random_number = random.random()

                        if random_number > scroll_chances:
                            # Swipe the screen from bottom to top
                            activity_handler.scroll(0.3)
                        elif random_number < like_chances:
                            activity_handler.like_post()
                            if random_number < comment_chances:
                                activity_handler.comment_on_post()
                                activity_handler.scroll(0.3)

                        time.sleep(interval)

                    d.press("back")
                    time.sleep(4)

    time.sleep(2)
    d.app_stop("com.instagram.android")
    print("Finished performing random activity")


def account_growth_handler(device):
    d = u2.connect(device)
    account_handler = AccountHandler(d)
    growth_handler = GrowthHandler(d)

    accounts = account_handler.get_all_accounts()

    for account in accounts:
        d.app_start("com.instagram.android", activity=".activity.MainTabActivity")
        account_handler.switch_account(account)

        if config_data["follow"]:
            growth_handler.follow_accounts()

        if config_data["like"] or config_data["comment"]:
            growth_handler.promote_accounts()

        time.sleep(8)
        random_activity(d, 60 * RANDOM_ACTIVITY_TIME)

        d.app_stop("com.instagram.android")
        time.sleep(120)
    print("Finished promoting accounts")


def content_upload_handler(device):
    d = u2.connect(device)
    d.dump_hierarchy()  # As ADB can cause issues otherwise
    pc_folder_path = os.path.join(".", "content")

    gdrive_handler = GDriveHandler(pc_folder_path)
    account_handler = AccountHandler(d)

    accounts = [
        (account, folder_id)
        for account, folder_id in account_config["devices"].get(device, {}).items()
        if folder_id != "N/A"
    ]

    content = {account: [] for account, folder_id in accounts}

    for account, folder_id in accounts:
        content_on_account = gdrive_handler.get_all_media_files(folder_id)
        content[account] = content_on_account

    while any(content.values()):
        for account, folder_id in accounts:
            media_list = content[account]
            d.app_start("com.instagram.android", activity=".activity.MainTabActivity")
            time.sleep(2)
            account_handler.switch_account(account)

            if media_list:
                media = media_list[0]
                print(
                    f"Downloading {media['name']} for account: {account} on device: {device}."
                )
                pc_media_path = gdrive_handler.download_files(media)

                file_handler = FileUploader(pc_media_path)
                android_media_path = file_handler.transfer_file_to_device(d)
                try:
                    if media["name"].startswith("STORY_"):
                        file_handler.upload_story(
                            d, android_media_path, media["media_type"]
                        )
                    elif media["media_type"] == "video":
                        file_handler.upload_reel(d, android_media_path)
                    elif media["media_type"] == "image":
                        file_handler.upload_post(d, android_media_path)
                except Exception as e:
                    print(f"Error: {e}")
                print(f"{media['name']}' uploaded for account '{account}'.")

                # Remove the uploaded video from the account's video list
                content[account] = media_list[1:]
                time.sleep(15)

                random_activity(d, 60 * RANDOM_ACTIVITY_TIME)
                time.sleep(120)
        d.app_stop("com.instagram.android")

    print(f"Finished uploading content from device: {device}")


def main():
    connected_devices = [device.serial for device in adbutils.adb.device_list()]
    choice = input("1. Post content\n2. Grow accounts\nEnter your choice: ")

    if choice == "1":
        if len(connected_devices) == 0:
            print("No devices connected!")
        else:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(connected_devices)
            ) as executor:
                executor.map(content_upload_handler, connected_devices)
    elif choice == "2":
        if len(connected_devices) == 0:
            print("No devices connected!")
        else:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(connected_devices)
            ) as executor:
                # Pass the instances as arguments to the threaded function
                executor.map(account_growth_handler, connected_devices)
    else:
        print("Error! Invalid choice, please try again!")


main()

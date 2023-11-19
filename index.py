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

RANDOM_ACTIVITY_TIME = 60

resource_ids = {"home_button": "com.instagram.android:id/feed_tab"}


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


def split_content_chunks(connected_devices, videos):
    # Get total number of accounts at the start to divide into chunks
    total_number_of_accounts = 0
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(connected_devices)
    ) as executor:
        # Create a separate instance for each device inside the thread
        instances = [AccountHandler(device) for device in connected_devices]

        # Use a lambda function to call get_all_accounts on each instance
        results = list(
            executor.map(
                lambda instance: instance.get_all_accounts(),
                instances,
            )
        )

    # Calculate total number of videos and average videos per account
    total_number_of_videos = len(videos)
    total_number_of_accounts = sum(len(result) for result in results)
    average_videos_per_account = total_number_of_videos / total_number_of_accounts

    # Create video chunks based on the number of accounts on each device
    content_chunks = []
    for result in results:
        num_videos_for_device = int(average_videos_per_account * len(result))
        content_chunks.append(videos[:num_videos_for_device])
        videos = videos[num_videos_for_device:]

    return content_chunks


def account_growth_handler(d):
    account_handler = AccountHandler(d)
    growth_handler = GrowthHandler(d)

    accounts = account_handler.get_all_accounts()

    for account in accounts:
        account_handler.switch_account(account)
        growth_handler.follow_accounts()
        growth_handler.promote_accounts()
        time.sleep(8)


def content_upload_handler(d, chunk):
    pc_folder_path = "./videos"
    gdrive_handler = GDriveHandler(pc_folder_path)
    account_handler = AccountHandler(d)

    index = 0
    accounts = account_handler.get_all_accounts()
    num_of_accounts = len(accounts)
    num_of_posts = len(chunk)

    for content in chunk:
        # Switch account for each iteration
        current_account = accounts[index % num_of_accounts]
        account_handler.switch_account(current_account)

        pc_vid_path = gdrive_handler.download_files(content)
        file_handler = FileUploader(pc_vid_path)

        android_vid_path = file_handler.transfer_file_to_device(d)
        file_handler.upload_reel(d, android_vid_path)

        random_activity(d)
        index += 1
        num_of_posts -= 1
        time.sleep(1500)


def main():
    pc_folder_path = "./videos"
    gdrive_handler = GDriveHandler(pc_folder_path)

    connected_devices = [
        u2.connect(device.serial) for device in adbutils.adb.device_list()
    ]
    videos = gdrive_handler.get_all_videos()
    choice = input("1. Upload videos\n2. Grow accounts\nEnter your choice: ")

    if choice == "1":
        content_chunks = split_content_chunks(connected_devices, videos)
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(connected_devices)
        ) as executor:
            executor.map(content_upload_handler, connected_devices, content_chunks)
    elif choice == "2":
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(connected_devices)
        ) as executor:
            # Pass the instances as arguments to the threaded function
            executor.map(account_growth_handler, connected_devices)
    else:
        print("Error! Invalid choice, please try again!")


main()

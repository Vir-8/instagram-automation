import time
import uiautomator2 as u2
from uiautomator2 import Device
import random
from gdrive_handler import GDriveHandler
from file_uploader import FileUploader
from growth_handler import GrowthHandler

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


def main():
    d = u2.connect()
    print(d.dump_hierarchy())  # As UIAutomator2 can cause issues otherwise

    pc_folder_path = "./videos"
    gdrive_handler = GDriveHandler(pc_folder_path)

    upload_videos = input("Do you want to upload videos? (true/false): ")

    if upload_videos == "true":
        video_files = gdrive_handler.get_all_videos()

        for video in video_files:
            pc_vid_path = gdrive_handler.download_files(video)
            file_handler = FileUploader(pc_vid_path)

            android_vid_path = file_handler.transfer_file_to_device(d)
            file_handler.upload_reel(d, android_vid_path)

            random_activity(d)

            time.sleep(1500)
    else:
        growth_handler = GrowthHandler(d)
        growth_handler.follow_accounts()
        growth_handler.promote_accounts()


main()

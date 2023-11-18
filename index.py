import time
import uiautomator2 as u2
from uiautomator2 import Device
import random
from gdrive_handler import GDriveHandler
from file_uploader import FileUploader
from growth_handler import GrowthHandler

RANDOM_ACTIVITY_TIME = 30


def random_activity(d: Device):
    print(f"Performing random activity on device: {d.serial}")

    # Click on home in case home isn't open
    d(resourceId="com.instagram.android:id/feed_tab").click()
    time.sleep(2)

    # Perform random activity for a set time, scrolling or liking at random intervals
    total_duration = RANDOM_ACTIVITY_TIME
    probability = 0.5

    # Get the screen size
    screen_size = d.window_size()
    screen_size_x = screen_size[0]
    screen_size_y = screen_size[1]

    # Start time of the loop
    start_time = time.time()

    # Main loop
    while time.time() - start_time < total_duration:
        # Generate random time interval and number
        interval = random.uniform(5, 15)
        random_number = random.random()
        print(f"random number is {random_number}")

        if random_number < probability:
            # Swipe the screen from bottom to top
            d.swipe(
                screen_size_x / 2,
                screen_size_y * 0.8,
                screen_size_x / 2,
                screen_size_y * 0.2,
                0.05,
            )

        time.sleep(interval)

    time.sleep(2)


def main():
    d = u2.connect()

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
        growth_handler = GrowthHandler
        growth_handler.follow_accounts(d)


main()

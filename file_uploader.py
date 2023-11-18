import os
import time

VIDEO_PATH_ON_DEVICE = "storage/emulated/0/Movies/"


class FileUploader:
    def __init__(self, file):
        self.file = file

    def transfer_file_to_device(self, d):
        # Save video on android in directory
        d.push(self.file, f"/{VIDEO_PATH_ON_DEVICE}")

        # Remove ./ from video name and define video path on android device
        local_video_path = (
            f"file:///{VIDEO_PATH_ON_DEVICE}{self.file[len('videos/'):][2:]}"
        )
        time.sleep(3)
        return local_video_path

    def upload_story(self, d, path):
        d.shell(
            f"am start -a android.intent.action.SEND -t video/* --eu android.intent.extra.STREAM {path} com.instagram.android"
        )
        d(text="Stories").click()
        time.sleep(2)

        if d(resourceId="android:id/button_once").exists():
            d(resourceId="android:id/button_once").click()

        print("uploaded")

    def upload_reel(self, d, path):
        d.shell(
            f"am start -a android.intent.action.SEND -t video/* --eu android.intent.extra.STREAM {path} com.instagram.android"
        )
        if d(text="Reels").exists():
            d(text="Reels").click()
        else:
            d(description="Reels").click()

        if d(resourceId="android:id/button_once").exists():
            d(resourceId="android:id/button_once").click()
        time.sleep(12)

        # Popup that says "videos will be uploaded as reels instead of posts"
        if d(text="OK", resourceId="com.instagram.android:id/primary_action").exists():
            d(text="OK", resourceId="com.instagram.android:id/primary_action").click()
            time.sleep(2)

        # Click next button
        if d(
            description="Next",
            resourceId="com.instagram.android:id/clips_right_action_button",
        ).exists():
            d(
                description="Next",
                resourceId="com.instagram.android:id/clips_right_action_button",
            ).click()
            time.sleep(2)

        time.sleep(6)

        # upload the reel
        if d(resourceId="com.instagram.android:id/share_button").exists():
            d(resourceId="com.instagram.android:id/share_button").click()
            time.sleep(2)

        # Popup about privacy, reels being visible to others
        if d(
            resourceId="com.instagram.android:id/clips_download_privacy_nux_button"
        ).exists():
            d(
                resourceId="com.instagram.android:id/clips_download_privacy_nux_button"
            ).click()
            time.sleep(2)
        elif d(
            resourceId="com.instagram.android:id/clips_nux_sheet_share_button"
        ).exists():
            print("here")
            d(
                resourceId="com.instagram.android:id/clips_nux_sheet_share_button"
            ).click()

        print("uploaded reel")

    def upload_post(self, d, path):
        d.shell(
            f"am start -a android.intent.action.SEND -t video/* --eu android.intent.extra.STREAM {path} com.instagram.android"
        )
        d(text="Feed").click()
        time.sleep(2)

        if d(resourceId="android:id/button_once").exists():
            d(resourceId="android:id/button_once").click()
        print("uploaded")

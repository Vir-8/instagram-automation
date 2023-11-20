import os
import time

VIDEO_PATH_ON_DEVICE = "storage/emulated/0/Movies/"

resource_ids = {
    "just_once_button": "android:id/button_once",
    "video_reel_popup_ok": "com.instagram.android:id/primary_action",
    "reel_upload_next": "com.instagram.android:id/clips_right_action_button",
    "reel_upload_share": "com.instagram.android:id/share_button",
    "reel_privacy_popup_share_1": "com.instagram.android:id/clips_download_privacy_nux_button",
    "reel_privacy_popup_share_2": "com.instagram.android:id/clips_nux_sheet_share_button",
}


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

        if d(resourceId=resource_ids["just_once_button"]).exists():
            d(resourceId=resource_ids["just_once_button"]).click()

        print("uploaded")

    def upload_reel(self, d, path):
        d.shell(
            f"am start -a android.intent.action.SEND -t video/* --eu android.intent.extra.STREAM {path} com.instagram.android"
        )
        if d(text="Reels").exists():
            d(text="Reels").click()
        elif d(description="Reels").exists():
            d(description="Reels").click()

        if d(resourceId=resource_ids["just_once_button"]).exists():
            d(resourceId=resource_ids["just_once_button"]).click()
        time.sleep(12)

        # Popup that says "videos will be uploaded as reels instead of posts"
        if d(text="OK", resourceId=resource_ids["video_reel_popup_ok"]).exists():
            d(text="OK", resourceId=resource_ids["video_reel_popup_ok"]).click()
            time.sleep(2)

        # Click next button
        d(
            description="Next",
            resourceId=resource_ids["reel_upload_next"],
        ).click()
        time.sleep(6)

        # upload the reel
        if d(resourceId=resource_ids["reel_upload_share"]).exists():
            d(resourceId=resource_ids["reel_upload_share"]).click()
            time.sleep(2)

        # Popup about privacy, reels being visible to others
        if d(resourceId=resource_ids["reel_privacy_popup_share_1"]).exists():
            d(resourceId=resource_ids["reel_privacy_popup_share_1"]).click()
            time.sleep(2)
        elif d(resourceId=resource_ids["reel_privacy_popup_share_2"]).exists():
            d(resourceId=resource_ids["reel_privacy_popup_share_2"]).click()

        print("Uploaded reel.")

    def upload_post(self, d, path):
        d.shell(
            f"am start -a android.intent.action.SEND -t video/* --eu android.intent.extra.STREAM {path} com.instagram.android"
        )
        d(text="Feed").click()
        time.sleep(2)

        if d(resourceId=resource_ids["just_once_button"]).exists():
            d(resourceId=resource_ids["just_once_button"]).click()
        print("uploaded")

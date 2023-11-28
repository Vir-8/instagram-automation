import os
import time
import json

VIDEO_PATH_ON_DEVICE = "storage/emulated/0/Movies/"

# Load configuration from config.json
config_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "config.json"
)

with open(config_path, "r") as config_file:
    config = json.load(config_file)

captions = config["captions"]

resource_ids = {
    "just_once_button": "android:id/button_once",
    "feed_right_arrow": "com.instagram.android:id/save",
    "feed_next": "com.instagram.android:id/next_button_textview",
    "feed_remix_popup_ok": "com.instagram.android:id/bb_primary_action",
    "feed_share": "com.instagram.android:id/next_button_textview",
    "close_friends_not_now": "com.instagram.android:id/auxiliary_button",
    "video_story_popup_ok": "com.instagram.android:id/primary_button",
    "video_reel_popup_ok": "com.instagram.android:id/primary_action",
    "reel_upload_next": "com.instagram.android:id/clips_right_action_button",
    "reel_upload_share": "com.instagram.android:id/share_button",
    "reel_privacy_popup_share_1": "com.instagram.android:id/clips_download_privacy_nux_button",
    "reel_privacy_popup_share_2": "com.instagram.android:id/clips_nux_sheet_share_button",
    "post_caption_input": "com.instagram.android:id/caption_text_view",
    "reel_caption_input": "com.instagram.android:id/caption_input_text_view",
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

    def upload_story(self, d, path, type):
        if type == "image":
            d.shell(
                f"am start -a android.intent.action.SEND -t image/* --eu android.intent.extra.STREAM '{path}' com.instagram.android"
            )
        elif type == "video":
            d.shell(
                f"am start -a android.intent.action.SEND -t video/* --eu android.intent.extra.STREAM '{path}' com.instagram.android"
            )
        time.sleep(4)
        d(text="Stories").click()

        time.sleep(4)
        if d(resourceId=resource_ids["just_once_button"]).exists():
            d(resourceId=resource_ids["just_once_button"]).click()

        # Popup that says "introducing longer stories..."
        if d(text="OK", resourceId=resource_ids["video_story_popup_ok"]).exists():
            d(text="OK", resourceId=resource_ids["video_story_popup_ok"]).click()
            time.sleep(2)

        if d(resourceId=resource_ids["close_friends_not_now"], text="Not now").exists():
            d(resourceId=resource_ids["close_friends_not_now"], text="Not now").click()

        time.sleep(8)
        d(description="Share to your story").click()

        time.sleep(5)
        # Another story popup after upload
        if d(text="OK", resourceId=resource_ids["video_story_popup_ok"]).exists():
            d(text="OK", resourceId=resource_ids["video_story_popup_ok"]).click()
            time.sleep(2)

        print("Uploaded story!")

    def upload_reel(self, d, path, name):
        d.shell(
            f"am start -a android.intent.action.SEND -t video/* --eu android.intent.extra.STREAM '{path}' com.instagram.android"
        )
        time.sleep(4)

        if d(text="Reels").exists():
            d(text="Reels").click()
        elif d(description="Reels").exists():
            d(description="Reels").click()
        time.sleep(4)

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

        # Add caption if available
        if name in captions:
            caption = captions[name]
            caption_text_area = d(resourceId=resource_ids["reel_caption_input"])
            caption_text_area.set_text(f"{caption}")
            time.sleep(2)
            d.press("back")
            time.sleep(2)

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

    def upload_post(self, d, path, name):
        d.shell(
            f"am start -a android.intent.action.SEND -t image/* --eu android.intent.extra.STREAM '{path}' com.instagram.android"
        )
        time.sleep(4)
        d(text="Feed").click()

        time.sleep(4)

        if d(resourceId=resource_ids["just_once_button"]).exists():
            d(resourceId=resource_ids["just_once_button"]).click()

        # First right arrow
        d(resourceId=resource_ids["feed_right_arrow"], description="Next").click()
        time.sleep(2)

        d(resourceId=resource_ids["feed_next"], description="Next").click()
        time.sleep(8)

        if d(resourceId=resource_ids["feed_remix_popup_ok"], text="OK").exists():
            d(resourceId=resource_ids["feed_remix_popup_ok"], text="OK").click()
            time.sleep(3)

        # Add caption if available
        if name in captions:
            caption = captions[name]
            caption_text_area = d(resourceId=resource_ids["post_caption_input"])
            caption_text_area.set_text(f"{caption}")
            time.sleep(2)
            d.press("back")
            time.sleep(2)

        d(resourceId=resource_ids["feed_share"], text="Share").click()
        print("Posted!")

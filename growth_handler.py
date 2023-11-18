import os
import time
import json

# Read the JSON file
with open("config.json", "r") as file:
    config_data = json.load(file)

# Access the array from the config data
list_of_accounts = config_data.get("list_of_accounts", [])


class GrowthHandler:
    def __init__(self):
        pass

    def follow_accounts(d):
        for account in list_of_accounts:
            d(resourceId="com.instagram.android:id/search_tab").click()
            d(resourceId="com.instagram.android:id/search_tab").click()

            d(resourceId="com.instagram.android:id/action_bar_search_edit_text").click()
            d(
                resourceId="com.instagram.android:id/action_bar_search_edit_text"
            ).set_text(f"{account}")

            time.sleep(3)
            d(
                resourceId="com.instagram.android:id/row_search_user_username",
                text=f"{account}",
            ).click()

            time.sleep(4)
            d(
                resourceId="com.instagram.android:id/profile_header_follow_button"
            ).click()

            time.sleep(5)

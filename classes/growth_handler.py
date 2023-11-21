import time
import json
import random
import os

# Get the current script's directory
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the path to the config.json file
config_path = os.path.join(script_dir, "..", "config.json")
with open(config_path, "r") as file:
    config_data = json.load(file)

# Access the array from the config data
list_of_accounts = config_data.get("list_of_accounts", [])

with open("comments.json", "r") as file:
    comments = json.load(file)


resource_ids = {
    "search_button": "com.instagram.android:id/search_tab",
    "search_bar": "com.instagram.android:id/action_bar_search_edit_text",
    "search_account": "com.instagram.android:id/row_search_user_username",
    "like_button": "com.instagram.android:id/row_feed_button_like",
    "comment_button": "com.instagram.android:id/row_feed_button_comment",
    "comment_input": "com.instagram.android:id/layout_comment_thread_edittext",
    "post_comment": "com.instagram.android:id/layout_comment_thread_post_button_click_area",
    "follow_button": "com.instagram.android:id/profile_header_follow_button",
}


class GrowthHandler:
    def __init__(self, d):
        self.d = d
        pass

    def find_account(self, account):
        d = self.d
        d(resourceId=resource_ids["search_button"]).click()
        d(resourceId=resource_ids["search_button"]).click()

        d(resourceId=resource_ids["search_bar"]).click()
        d(resourceId=resource_ids["search_bar"]).set_text(f"{account}")
        time.sleep(3)

        d(
            resourceId=resource_ids["search_account"],
            text=f"{account}",
        ).click()
        time.sleep(4)

    def follow_accounts(self):
        d = self.d
        for account in list_of_accounts:
            self.find_account(account)
            if d(
                resourceId=resource_ids["follow_button"],
                text="Follow",
            ).exists():
                d(
                    resourceId=resource_ids["follow_button"],
                    text="Follow",
                ).click()

            time.sleep(5)

    def like_post(self):
        d = self.d
        like_button = d(resourceId=resource_ids["like_button"])

        if like_button.exists():
            like_button.click()
        else:
            self.scroll(0.08)
            like_button.click() if like_button.exists() else print("Error liking post.")

    def comment_on_post(self):
        d = self.d
        # Select a comment at random
        random_comment = random.choice(comments)

        comment_button = d(resourceId=resource_ids["comment_button"])
        comment_text_area = d(resourceId=resource_ids["comment_input"])
        post_comment_button = d(resourceId=resource_ids["post_comment"])

        comment_button.click()
        comment_text_area.set_text(f"{random_comment}")
        post_comment_button.click()

        time.sleep(3)
        d.press("back")

        time.sleep(1)
        d.press("back")

    def scroll(self, scroll_percentage):
        d = self.d
        # Get the screen size
        screen_width, screen_height = d.window_size()

        # Calculate the scroll coordinates
        start_x, start_y = screen_width // 2, int(screen_height * 0.8)
        end_x, end_y = screen_width // 2, int(screen_height * (0.8 - scroll_percentage))

        d.swipe(start_x, start_y, end_x, end_y, 0.03)

    def promote_accounts(self):
        d = self.d
        for account in list_of_accounts:
            self.find_account(account)

            num_of_posts = 9
            num_columns = 3

            # Create a list of all possible post positions
            all_posts = [
                (row, col)
                for row in range(1, (num_of_posts - 1) // num_columns + 2)
                for col in range(
                    1, min(num_of_posts - (row - 1) * num_columns, num_columns) + 1
                )
            ]

            # Shuffle the list to randomize the order
            random.shuffle(all_posts)

            # Iterate through the randomly selected photos
            for row, col in all_posts:
                partial_description = f"row {row}, column {col}"

                # Maximum number of attempts to find the post
                max_attempts = 3

                # Iterate through attempts
                for attempt in range(1, max_attempts + 1):
                    # Fetch all elements with the description attribute using XPath
                    elements_with_description = d.xpath("//*[@content-desc]").all()
                    post_found = False

                    # Iterate through the elements and find the one that matches (case-insensitive)
                    for element in elements_with_description:
                        if (
                            partial_description.lower()
                            in element.info["contentDescription"].lower()
                        ):
                            element.click()
                            post_found = True
                            time.sleep(2)

                            if config_data["like"]:
                                self.like_post()
                            # Probability of execution (20%)
                            if config_data["comment"]:
                                comment_probability = (
                                    config_data["comment_probability"]
                                ) / 100

                                # Check if the function should be executed based on the probability
                                if random.random() < comment_probability:
                                    self.comment_on_post()
                                break

                    # If the element is not found, scroll and retry
                    if not post_found:
                        self.scroll(0.08)  # 0.2 for 20% of screen height
                        time.sleep(1)  # Wait for the UI to update after the scroll
                    else:
                        # Break the outer loop if the element is found
                        break

                # Wait for a moment to make sure the action is completed
                time.sleep(2)
                d.press("back")

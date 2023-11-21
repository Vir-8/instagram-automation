import time

resource_ids = {
    "profile_button": "com.instagram.android:id/profile_tab",
    "account_arrow": "com.instagram.android:id/action_bar_little_icon_container",
    "account_element": "com.instagram.android:id/row_user_textview",
}


class AccountHandler:
    def __init__(self, d):
        self.d = d

    def get_all_accounts(self):
        d = self.d

        # Open instagram
        d.app_start("com.instagram.android", activity=".activity.MainTabActivity")
        time.sleep(2)

        # Open profile page
        d(resourceId=resource_ids["profile_button"]).click()
        time.sleep(1)

        # Open accounts menu
        d(resourceId=resource_ids["account_arrow"]).click()

        time.sleep(1)

        # Get number of accounts
        account_elements = d(resourceId=resource_ids["account_element"])
        number_of_accounts = len(account_elements) - 1

        accounts = [0] * number_of_accounts

        for i in range(number_of_accounts):
            element = account_elements[i]
            name = element.info["text"]
            accounts[i] = name

        d.press("back")
        return accounts

    def switch_account(self, account):
        d = self.d

        # Open profile page
        d(resourceId=resource_ids["profile_button"]).click()
        time.sleep(1)

        # Open accounts menu
        d(resourceId=resource_ids["account_arrow"]).click()

        time.sleep(1)

        # Get number of accounts
        d(resourceId=resource_ids["account_element"], text=account).click()
        time.sleep(3)

        d.press("back")
        time.sleep(4)

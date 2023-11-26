import os
import json
import uiautomator2 as u2
import adbutils
from classes.gdrive_handler import GDriveHandler
from classes.file_uploader import FileUploader
from classes.growth_handler import GrowthHandler
from classes.account_handler import AccountHandler
import concurrent.futures
import time


def handle_permissions(d):
    d.dump_hierarchy()  # Since ADB can cause issues otherwise

    # Grant permissions
    list_of_permissions = [
        "READ_EXTERNAL_STORAGE",
        "WRITE_EXTERNAL_STORAGE",
        "READ_MEDIA_IMAGES",
        "READ_MEDIA_VIDEO",
        "READ_MEDIA_VISUAL_USER_SELECTED",
        "READ_MEDIA_AUDIO",
        "READ_PHONE_STATE",
        "CAMERA",
        "RECORD_AUDIO",
        "ACCESS_FINE_LOCATION",
        "ACCESS_COARSE_LOCATION",
        "ACCESS_BACKGROUND_LOCATION",
        "ACCESS_MEDIA_LOCATION",
    ]

    shell_command = ""

    for permission in list_of_permissions:
        shell_command += (
            f"pm grant com.instagram.android android.permission.{permission};"
        )

    try:
        print("Granting permissions...")
        d.shell(shell_command)
        time.sleep(15)
    except Exception as e:
        print(f"Error granting permissions: {e}")


def find_accounts_on_device(connected_device, device):
    connected_device.app_start(
        "com.instagram.android", activity=".activity.MainTabActivity"
    )

    # Click on Cancel button if it exists
    if connected_device(className="android.widget.Button", text="Cancel").exists():
        connected_device(className="android.widget.Button", text="Cancel").click()
        time.sleep(2)

    # Click on Don't allow button if it exists
    if connected_device(className="android.widget.Button", text="Don't allow").exists():
        connected_device(className="android.widget.Button", text="Don't allow").click()

    account_handler = AccountHandler(connected_device)
    accounts = account_handler.get_all_accounts()
    return device, accounts


def create_account_config(results):
    account_config = {
        "total_number_of_devices": len(results),
        "total_number_of_accounts": 0,
        "devices": {},
    }

    for device, accounts in results:
        account_config["devices"][device] = {account: "N/A" for account in accounts}
        account_config["total_number_of_accounts"] += len(accounts)

    return account_config


def verify_google_drive_folders(account_config):
    drive_handler = GDriveHandler("./content")
    account_folders = drive_handler.get_all_folders()

    unavailable_folders = 0
    unused_folders = 0

    for device, device_accounts in account_config["devices"].items():
        for account, folder_id in device_accounts.items():
            for folder in account_folders:
                if folder["name"] == account:
                    # Associate the account with the folder ID
                    account_config["devices"][device][account] = folder["id"]
                    break

    for device, device_accounts in account_config["devices"].items():
        for account, folder_id in device_accounts.items():
            if folder_id == "N/A":
                unavailable_folders += 1
                print(
                    f"Warning: Folder for account '{account}' on device '{device}' is not available."
                )

    for folder in account_folders:
        exists = False
        for device, device_accounts in account_config["devices"].items():
            for account, folder_id in device_accounts.items():
                if folder["name"] == account:
                    exists = True
                    break

            if exists:
                break

        unused_folders += 1 if not exists else 0

    num_available_folders = len(account_folders) - (
        unavailable_folders + unused_folders
    )
    if len(account_folders) > num_available_folders:
        print(
            f"Warning: {len(account_folders) - num_available_folders} unused folder(s) found in Google drive."
        )

    # Save the results in account_config.json
    with open("account_config.json", "w") as json_file:
        json.dump(account_config, json_file, indent=4)


def main():
    devices = [device.serial for device in adbutils.adb.device_list()]
    connected_devices = [
        u2.connect(device.serial) for device in adbutils.adb.device_list()
    ]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Concurrently execute find_accounts_on_device for each device
        executor.map(handle_permissions, connected_devices)
        results = list(
            executor.map(find_accounts_on_device, connected_devices, devices)
        )

    # Task 2: Create 'account_config.json' file
    account_config = create_account_config(results)

    # Task 3: Verify whether a Google Drive folder exists for each account
    verify_google_drive_folders(account_config)

    print("Successfully generated account_config.json")


main()

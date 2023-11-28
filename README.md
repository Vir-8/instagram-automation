# Instagram Automation

## setup.py

This setup script initializes and configures the Instagram automation environment. It performs the following key tasks:

1. **Handle Permissions:**

   - Grants necessary permissions to the Instagram application using the `uiautomator2` library.
   - Permissions include storage access, camera usage, location permissions, and more.

2. **Find Accounts on Connected Devices:**

   - Identifies Instagram accounts available on each connected device.
   - Utilizes concurrent threads to enhance efficiency.

3. **Create 'account_config.json':**

   - Generates a configuration file (`account_config.json`) containing information about connected devices and associated Instagram accounts.
   - Provides a total count of devices and accounts for reference.

4. **Verify Google Drive Folders:**

   - Ensures that Google Drive folders are associated with Instagram accounts.
   - Warns about any unavailable or unused folders and prints relevant messages.

### Instructions:

1. **Run the Script:**

   - Execute the script to perform the setup tasks.
   - Review the console output for any warnings or messages.

2. **Important Notes:**

   - This script assumes a working ADB environment and a connected Android device.
   - Ensure that the Google Drive folder structure matches the expected configuration.

## index.py

This script automates Instagram activities such as content uploading and account growth. The primary functionalities include:

1. **Content Upload**

   - Downloads media content from Google Drive for each connected device and account.
   - Uploads stories, reels (videos), and posts (images) to Instagram.
   - Performs random activities on the app during and after uploads to simulate user engagement.

2. **Account Growth**

   - Follows accounts based on predefined configurations.
   - Likes and comments on posts to promote the connected accounts.
   - Conducts random activities to mimic natural user behavior.

### Instructions:

1. **Configuration:**

   - Configure the script using `config.json`.
   - Adjust settings such as random activity time, follow/like/comment preferences, etc.
   - Ensure that your post/reel captions are correctly configured in `config.json`, along with the file extension in the name as shown.

2. **Run the Script:**

   - Execute the script and choose the desired operation: content upload or account growth.
   - The script supports multiple connected devices, utilizing concurrent threads for efficient execution.

3. **Important Notes:**

   - Random activity is carried out in the 'explore' tab.
   - During random activity, posts/reels are selected in a random order from the first 3 rows.

## Important Notes:

- Ensure that `uiautomator2`, `adbutils`, and other dependencies are installed.
- Make sure that Google Drive folder ID is properly configured in `config.json` and run setup.py beforehand.

**Caution:** Always comply with Instagram's policies to avoid potential account restrictions.

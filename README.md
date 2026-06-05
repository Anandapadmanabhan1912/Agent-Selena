# YouTube Music Playlist Downloader

An automated pipeline to extract all song URLs from a YouTube Music playlist and download them as MP3s via browser automation using Selenium and Brave/Chrome.

---

## Features

- **Automated Extraction**: Scroll through the YouTube Music playlist to dynamically load and extract all track URLs.
- **Batched Downloads**: Automates the conversion and downloading of songs through a conversion service.
- **Popup & Tab Management**: Automatically closes redirection and popup tabs spawned during conversion/downloading.
- **Dynamic Download Monitoring**: Monitors the download directory and waits until the file is fully downloaded (`.crdownload` temporary files are cleared) before moving to the next track.
- **Verbose Console Output**: Real-time console logs outlining current browser state, scrolling progress, extraction count, conversion steps, and download monitoring.

---

## Prerequisites

1. **Python 3.7+**
   - Download and install from [python.org](https://www.python.org/downloads/). Ensure you check the option to **Add Python to PATH** during installation.

2. **Web Browser**
   - **Brave Browser** (Default): Install from [brave.com](https://brave.com/).
   - Alternatively, you can use **Google Chrome**.

3. **Required Python Libraries**
   - Install Selenium via pip:
     ```bash
     pip install selenium
     ```

---

## Configuration

All configuration paths and settings are managed in [config.json](file:///d:/AgentSelena/config.json). If this file does not exist, it will be automatically created with default values when you run the pipeline.

```json
{
    "browser_path": "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    "profile_path": "C:\\Users\\<YourUsername>\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data",
    "download_path": "C:\\Users\\<YourUsername>\\Downloads\\Music",
    "temp_file": "playlist_urls.txt",
    "download_site": "https://v3.y2mate.nu/",
    "headless": true
}
```

> [!WARNING]
> Since `config.json` is a JSON file, you must escape all backslashes in Windows file paths by using double backslashes (`\\`). E.g., `"C:\\Program Files\\..."`.

---

### How to Retrieve Configuration Paths

#### 1. Browser Path (`browser_path`)
To find the exact path to your browser executable:
1. Search for **Brave** (or **Chrome**) in the Windows Start menu.
<img width="628" height="385" alt="image" src="https://github.com/user-attachments/assets/bdde984e-cf36-491f-9666-90898835e29b" />

2. Right-click the browser icon, hover over **More**, and select **Open file location**. (If it opens a folder of shortcuts, right-click the browser shortcut and select **Properties**).
3. Under the **Shortcut** tab, copy the path listed in the **Target** field.
4. Paste it into `config.json`, replacing single backslashes `\` with double backslashes `\\`.

*Typical defaults:*
- **Brave**: `C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe`
- **Chrome**: `C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe`

#### 2. Profile User Data Path (`profile_path`)
To inherit cookies, logins, and extensions (like ad blockers) from your everyday browser session:
1. Open your browser and navigate to `brave://version` (or `chrome://version` for Chrome).
2. Look for the **Profile Path** row. E.g.:
   `C:\Users\YourUsername\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default`
3. Copy this path but **exclude the final `\Default` folder**.
4. The remaining part is your user data folder:
   `C:\Users\YourUsername\AppData\Local\BraveSoftware\Brave-Browser\User Data`
5. Paste it into `config.json` using double backslashes.

#### 3. Download Path (`download_path`)
This is the folder where downloaded files will be stored:
1. Open Windows File Explorer and navigate to the folder where you want your music saved.
2. Click on the folder address bar at the top of File Explorer.
3. Copy the full path.
4. Paste it into `config.json` using double backslashes. The script will automatically create this directory if it doesn't already exist.

#### 4. Headless Mode (`headless`)
- Set `"headless": true` to run the automation in the background.
- Set `"headless": false` to run with a visible browser window. This is highly recommended for troubleshooting or observing how the automation behaves.

---

## How to Run

1. Open a terminal/command prompt inside the repository folder:
   ```cmd
   cd d:\AgentSelena
   ```

2. Execute the script:
   ```cmd
   python pipeline.py
   ```

3. When prompted, enter a valid YouTube Music Playlist URL:
   ```text
   Enter YouTube Music Playlist URL: https://music.youtube.com/playlist?list=PL...
   ```

4. The pipeline will begin execution:
   - **Stage 1 (Extraction)**: Opens the playlist, scrolls to load all tracks, extracts unique URLs, and saves them to `playlist_urls.txt`.
   - **Stage 2 (Downloading)**: Iterates through the saved URLs, conversion is triggered on `https://v3.y2mate.nu/`, download is initialized, and completion is verified.

---

## Troubleshooting

- **Session/Profile Lock Error**: Close all running instances of Brave/Chrome before running the script. Since Selenium uses your main user profile, it cannot share the profile folder with another active browser process.
- **Download Timeout**: If download speeds are slow, you can increase the timeout limit in [module_file.py](file:///d:/AgentSelena/module_file.py) (currently set to 60 seconds).

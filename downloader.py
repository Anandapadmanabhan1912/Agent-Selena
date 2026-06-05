from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import shutil
import time

urls = [
    "https://music.youtube.com/watch?v=N4wK3NtVRT0",
    "https://music.youtube.com/watch?v=KrJ5c-Egz-U",
    # Add more URLs here.
]


import json

def load_config():
    config_path = "config.json"
    default_config = {
        "browser_path": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        "profile_path": r"C:\Users\bijur\AppData\Local\BraveSoftware\Brave-Browser\User Data",
        "download_path": r"C:\Users\bijur\Downloads\Music",
        "temp_file": "playlist_urls.txt",
        "download_site": "https://v3.y2mate.nu/",
        "headless": True
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                for key, val in default_config.items():
                    if key not in config:
                        config[key] = val
                return config
        except:
            pass
    return default_config

config = load_config()
DOWNLOAD_URL = config["download_site"]
BRAVE_EXE = config["browser_path"]
ORIGINAL_PROFILE = config["profile_path"]
DOWNLOAD_DIR = config["download_path"]
HEADLESS = config["headless"]

options = Options()
options.binary_location = BRAVE_EXE
options.add_argument(f"--user-data-dir={ORIGINAL_PROFILE}")
options.add_argument("--profile-directory=Default")

# Anti-detection flags
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

# Configure download preferences
prefs = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": False
}
options.add_experimental_option("prefs", prefs)

# Stability flags - CRITICAL to prevent crashes
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--disable-plugins")
options.add_argument("--disable-images")  # Reduce memory usage
if HEADLESS:
    options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)
main_window = driver.current_window_handle

try:
    
    for index, url in enumerate(urls, start=1):
        # Close any lingering popups from the previous iteration
        for handle in driver.window_handles:
            if handle != main_window:
                try:
                    driver.switch_to.window(handle)
                    driver.close()
                except:
                    pass
        driver.switch_to.window(main_window)

        print(f"[{index}/{len(urls)}] Downloading: {url}")
        driver.get(DOWNLOAD_URL)
        time.sleep(1)  # Give the page a moment to start loading

        # Wait for the main content to load
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "video")))

        url_input = driver.find_element(By.ID, "video")
        url_input.clear()
        url_input.send_keys(url)

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "download")))

        download_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.download[type='button']"))
        )
        download_button.click()

        time.sleep(3)  # Give time for popups to open
        
        # Clean up any new popups
        for handle in driver.window_handles:
            if handle != main_window:
                try:
                    driver.switch_to.window(handle)
                    driver.close()
                except:
                    pass
        driver.switch_to.window(main_window)

        time.sleep(7)  # Remaining time for download to finish
        print(f"  ✓ Finished download")
        driver.find_element(By.TAG_NAME, "body").send_keys("")  # Reset focus
        if index < len(urls):
            time.sleep(3)
except Exception as e:
    print(f"✗ An error occurred: {e}")
    import traceback
    traceback.print_exc()

finally:
    try:
        time.sleep(2)  # Keep browser open for a moment to see results
        driver.quit()
        print("\nBrowser closed.")
    except:
        pass
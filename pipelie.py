# Save this file as 'yt_downloader_pipeline.py'
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from module_file import YouTubePlaylistExtractor, MusicDownloader # Ensure classes are imported
import os
import json

def load_config():
    config_path = "config.json"
    default_config = {
        "browser_path": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        "profile_path": r"C:\Users\Profile1\AppData\Local\BraveSoftware\Brave-Browser\User Data",
        "download_path": r"C:\Users\Profile1\Downloads\Music",
        "temp_file": "playlist_urls.txt",
        "download_site": "https://v3.y2mate.nu/",
        "headless": True
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                # Ensure all default keys exist
                for key, val in default_config.items():
                    if key not in config:
                        config[key] = val
                return config
        except Exception as e:
            print(f"---> Warning: Could not read {config_path}. Using default configuration. Error: {e}")
            
    return default_config

def run_pipeline(playlist_url):
    config = load_config()
    BRAVE_EXE = config["browser_path"]
    PROFILE_DIR = config["profile_path"]
    DOWNLOAD_DIR = config["download_path"]
    TEMP_FILE = config["temp_file"]
    DOWNLOAD_SITE = config["download_site"]
    HEADLESS = config["headless"]

    print(f"Starting YT Music Downloader Pipeline for playlist: {playlist_url}")

    # Create download directory if it doesn't exist
    if not os.path.exists(DOWNLOAD_DIR):
        print(f"Creating download directory: {DOWNLOAD_DIR}")
        os.makedirs(DOWNLOAD_DIR)

    options = Options()
    options.binary_location = BRAVE_EXE
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--profile-directory=Default")
    
    # Config download preferences
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    
    # Anti-detection flags
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Performance & Stability flags
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-images")  # Reduces CPU/RAM usage significantly
    
    if HEADLESS:
        options.add_argument("--headless=new")
        
    driver = webdriver.Chrome(options=options)

    extracted_count = 0
    try:
        # Stage 1: Extraction
        print("\n[Stage 1/2] Extracting tracks from playlist...")
        extractor = YouTubePlaylistExtractor(driver=driver)
        urls = extractor.extract_urls(playlist_url)
        extracted_count = len(urls)
        extractor.save_to_file(urls, TEMP_FILE)

        if extracted_count > 0:
            # Stage 2: Downloading
            print(f"\n[Stage 2/2] Downloading {extracted_count} tracks...")
            downloader = MusicDownloader(download_dir=DOWNLOAD_DIR, driver=driver)
            downloader.download_list(urls, DOWNLOAD_SITE)
        else:
            print("\n⚠ No tracks extracted. Skipping download stage.")
        
    except Exception as e:
        print(f"\n❌ Pipeline execution encountered an error: {e}")
        try:
            screenshot_path = "error_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"Captured error screenshot: {os.path.abspath(screenshot_path)}")
        except Exception as se:
            print(f"Could not capture screenshot: {se}")
            
        try:
            source_path = "error_page_source.html"
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"Captured error page source: {os.path.abspath(source_path)}")
        except Exception as sse:
            print(f"Could not capture page source: {sse}")

        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except Exception as e:
            print(f"Error closing browser: {e}")
    
    print(f"\nPipeline Complete. Processed {extracted_count} songs. All tasks finished.")

if __name__ == "__main__":
    user_url = input("Enter YouTube Music Playlist URL: ").strip()
    run_pipeline(user_url)
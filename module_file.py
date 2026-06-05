import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class YouTubePlaylistExtractor:
    def __init__(self, binary_path=None, profile_path=None, driver=None):
        if driver:
            self.driver = driver
            self.should_close = False
        else:
            self.options = Options()
            if binary_path:
                self.options.binary_location = binary_path
            if profile_path:
                self.options.add_argument(f"--user-data-dir={profile_path}")
                self.options.add_argument("--profile-directory=Default")
            
            # Anti-detection flags
            self.options.add_argument("--disable-blink-features=AutomationControlled")
            self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            # Performance flags
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-dev-shm-usage")
            self.options.add_argument("--disable-images")
            
            self.driver = webdriver.Chrome(options=self.options)
            self.should_close = True

    def _scroll_to_bottom(self):
        """Internal helper to load all items in the playlist."""
        last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(1)  # Faster scrolling sleep
            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def extract_urls(self, playlist_url):
        """Extracts unique song URLs from the provided playlist."""
        self.driver.get(playlist_url)
        
        # Check for Google/YouTube Cookie Consent redirection
        time.sleep(2)
        current_url = self.driver.current_url
        if "consent.google" in current_url or "google.com/co" in current_url or "youtube.com/co" in current_url:
            print("  • Handling Google/YouTube Cookie Consent...")
            try:
                # Common CSS selectors for consent buttons
                consent_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Accept'], button[aria-label*='Agree'], button")
                accepted = False
                for btn in consent_buttons:
                    text = btn.text.lower()
                    if "accept all" in text or "agree" in text or "accept" in text or "agree to" in text:
                        btn.click()
                        accepted = True
                        break
                if not accepted and consent_buttons:
                    # Fallback to clicking the last button which is usually Accept/Agree
                    consent_buttons[-1].click()
                time.sleep(2)
            except Exception as e:
                pass

        wait = WebDriverWait(self.driver, 25)
        # Check for multiple possible tags representing loaded content
        selector = "ytmusic-playlist-shelf-renderer, ytmusic-responsive-list-item-renderer, ytmusic-shelf-renderer"
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

        print("  • Scrolling to load all tracks...")
        self._scroll_to_bottom()

        elements = self.driver.find_elements(By.CSS_SELECTOR, "ytmusic-responsive-list-item-renderer a[href*='watch?v=']")
        
        urls = set()
        for idx, el in enumerate(elements, 1):
            href = el.get_attribute("href")
            if href:
                # Strip the playlist parameter to get the clean video URL
                clean_url = href.split("&list=")[0]
                urls.add(clean_url)
        
        sorted_urls = sorted(list(urls))
        print(f"✓ Extracted {len(sorted_urls)} unique track URLs.")
        return sorted_urls

    def save_to_file(self, urls, filename="playlist_urls.txt"):
        """Saves the list of URLs to a text file."""
        with open(filename, "w", encoding="utf-8") as f:
            for url in urls:
                f.write(f"{url}\n")

    def close(self):
        if getattr(self, "should_close", True):
            self.driver.quit()


class MusicDownloader:
    def __init__(self, binary_path=None, profile_path=None, download_dir=None, driver=None):
        self.download_dir = download_dir
        if driver:
            self.driver = driver
            self.should_close = False
        else:
            options = Options()
            if binary_path:
                options.binary_location = binary_path
            if profile_path:
                options.add_argument(f"--user-data-dir={profile_path}")
                options.add_argument("--profile-directory=Default")
            
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            # Configure download path
            if download_dir:
                options.add_experimental_option("prefs", {
                    "download.default_directory": download_dir,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True
                })
            
            # Performance/Stability flags
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-images")
            
            self.driver = webdriver.Chrome(options=options)
            self.should_close = True

    def download_list(self, urls, target_site):
        """Processes a list of URLs and performs the download sequence."""
        wait = WebDriverWait(self.driver, 30)
        main_window = self.driver.current_window_handle

        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Downloading: {url}")
            try:
                # 1. Close any extra popup tabs/windows that are open
                open_handles = self.driver.window_handles
                if len(open_handles) > 1:
                    for handle in open_handles:
                        if handle != main_window:
                            try:
                                self.driver.switch_to.window(handle)
                                self.driver.close()
                            except Exception:
                                pass
                    self.driver.switch_to.window(main_window)

                # 2. Always navigate back to target site to start clean
                self.driver.get(target_site)

                # 3. Enter URL
                url_input = wait.until(EC.presence_of_element_located((By.ID, "video")))
                url_input.clear()
                url_input.send_keys(url)
                
                # 4. Submit
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_btn.click()
                
                # 5. Wait for and click download
                dl_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.download[type='button']")))
                dl_btn.click()
                
                time.sleep(3)  # Wait briefly for popups to trigger
                
                # Clean up popups immediately
                open_handles = self.driver.window_handles
                if len(open_handles) > 1:
                    for handle in open_handles:
                        if handle != main_window:
                            try:
                                self.driver.switch_to.window(handle)
                                self.driver.close()
                            except Exception:
                                pass
                    self.driver.switch_to.window(main_window)

                # Wait dynamically for download to complete if download_dir exists
                if self.download_dir and os.path.exists(self.download_dir):
                    start_time = time.time()
                    download_started = False
                    
                    # Wait up to 10 seconds for download to start (new file appears)
                    initial_files = set(os.listdir(self.download_dir))
                    new_filename = None
                    while time.time() - start_time < 10:
                        current_files = set(os.listdir(self.download_dir))
                        new_files = current_files - initial_files
                        if new_files:
                            download_started = True
                            new_filename = next(iter(new_files))
                            break
                        time.sleep(0.5)
                    
                    if download_started:
                        completion_start = time.time()
                        while time.time() - completion_start < 60:
                            current_list = os.listdir(self.download_dir)
                            crdownloads = [f for f in current_list if f.endswith(".crdownload") or f.endswith(".tmp")]
                            if not crdownloads:
                                current_files = set(os.listdir(self.download_dir))
                                final_files = current_files - initial_files
                                final_name = next(iter(final_files)) if final_files else new_filename
                                print(f"  ✓ Finished download: '{final_name}'")
                                break
                            time.sleep(1)
                        else:
                            print("  ⚠ Timeout waiting for download. Proceeding...")
                    else:
                        print("  ⚠ No file detected in download directory within 10 seconds. Proceeding...")
                        time.sleep(5)
                else:
                    time.sleep(9)
                
            except Exception as e:
                print(f"  ✗ Error processing {url}: {e}")

    def close(self):
        if getattr(self, "should_close", True):
            self.driver.quit()
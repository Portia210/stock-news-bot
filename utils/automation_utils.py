from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
import time
import os
import base64
import json
from pathlib import Path
import requests
from utils.logger_config import setup_logger
import sys



main_logger = setup_logger()

def check_internet_connection(func):
    """Decorator to check internet connection before executing a function"""
    # def wrapper(self, *args, **kwargs):
    #     try:
    #         # Disable SSL verification warnings
    #         import urllib3
    #         import urllib.request
    #         urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
    #         # Try to connect with SSL verification disabled
    #         with urllib.request.urlopen("https://meyazegs.btl.gov.il/", timeout=10) as response:
    #             status_code = response.getcode()
    #             if status_code == 200:
    #                 return func(self, *args, **kwargs)
    #             main_logger.warning(f"BTL website returned status code {response.status_code}")
    #             if hasattr(self, 'output_callback'):
    #                 self.output_callback(f"אזהרה, האתר החזיר קוד תגובה: {response.status_code}")
    #             return func(self, *args, **kwargs)
            
    #     except requests.RequestException as e:
    #         if hasattr(self, 'output_callback'):
    #             error_msg = str(e)
    #             if "SSLError" in error_msg:
    #                 main_logger.error("SSL Security error connecting to site")
    #                 self.output_callback("בעיית אבטחה בחיבור לאתר. נסה להתחבר שוב", "error")
    #             elif "ConnectTimeout" in error_msg:
    #                 main_logger.error("Connection timeout to site")
    #                 self.output_callback("החיבור לאתר איטי מדי. נא לנסות שוב", "error")
    #             elif "ConnectionError" in error_msg:
    #                 main_logger.error("Failed to connect to site")
    #                 self.output_callback("לא ניתן להתחבר לאתר. נא לבדוק את החיבור לאינטרנט", "error")
    #             else:
    #                 main_logger.error(f"Connection error: {error_msg}")
    #                 self.output_callback(f"שגיאה בהתחברות לאתר: {error_msg}", "error")
    #         return False
            
    #     except Exception as e:
    #         main_logger.error(f"Unexpected error in connection check: {str(e)}", exc_info=True)
    #         if hasattr(self, 'output_callback'):
    #             self.output_callback(f"שגיאה לא צפויה: {str(e)}", "error")
    #         return False
    # return wrapper
    return func


class Automation:
    CONFIG_FILE = "config.json"

    @staticmethod
    def get_output_dir():
        """Get output directory from config file or default to cwd"""
        try:
            config_path = Path(Automation.CONFIG_FILE)
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)
                    if "OUTPUT_DIR" in config:
                        path_from_config = os.path.abspath(config["OUTPUT_DIR"])
                        normalized_path_for_python = os.path.normpath(path_from_config)
                        return normalized_path_for_python
        except Exception:
            return os.getcwd()

    @staticmethod
    def start_chrome_driver(headless=False) -> webdriver.Chrome:
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--kiosk-printing")

            # Add SSL error handling options
            # chrome_options.add_argument('--ignore-certificate-errors')
            # chrome_options.add_argument('--ignore-ssl-errors')
            # chrome_options.add_argument('--ignore-certificate-errors-spki-list')
            # chrome_options.add_argument('--allow-insecure-localhost')

            if headless:
                # Add these options to properly handle headless mode
                chrome_options.add_argument("--headless=new")  # Use new headless mode
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--hide-scrollbars")
                chrome_options.add_argument("--mute-audio")
                # Add this to prevent any window from showing
                chrome_options.add_argument("--window-position=-32000,-32000")

            download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            # Create the directory if it doesn't exist
            os.makedirs(download_dir, exist_ok=True)

            chrome_options.add_experimental_option(
                "prefs",
                {
                    "download.default_directory": download_dir,
                    "plugins.always_open_pdf_externally": True,
                    "savefile.default_directory": download_dir,
                    "printing.print_preview_sticky_settings.appState": '{"recentDestinations":[{"id":"Save as PDF","origin":"local"}],"selectedDestinationId":"Save as PDF","version":2}',
                    "profile.default_content_settings.popups": 0,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True,
                },
            )

            # Add these options to prevent any UI from showing
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Add this to prevent timeout
            chrome_options.add_argument("--dns-prefetch-disable")

            # Get Chrome version and download matching ChromeDriver
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                winreg.CloseKey(key)
                
                # Extract major version
                major_version = version.split('.')[0]
                
                # Create drivers directory if it doesn't exist
                if getattr(sys, 'frozen', False):
                    # If we're running as a PyInstaller executable
                    base_path = os.path.dirname(sys.executable)
                else:
                    # If we're running as a Python script
                    base_path = os.path.dirname(os.path.abspath(__file__))
                
                drivers_dir = os.path.join(base_path, "drivers")
                os.makedirs(drivers_dir, exist_ok=True)
                
                # Check if we already have the correct version
                chromedriver_path = os.path.join(drivers_dir, f"chromedriver_{major_version}.exe")
                
                if not os.path.exists(chromedriver_path):
                    main_logger.info(f"Downloading ChromeDriver for Chrome version {major_version}")
                    # Download ChromeDriver from Google's servers
                    import urllib.request
                    import zipfile
                    import io
                    
                    # URL for ChromeDriver download
                    url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/win32/chromedriver-win32.zip"
                    
                    # Download and extract ChromeDriver
                    response = urllib.request.urlopen(url)
                    zip_data = io.BytesIO(response.read())
                    
                    with zipfile.ZipFile(zip_data) as zip_file:
                        # Extract chromedriver.exe from the zip
                        for file in zip_file.namelist():
                            if file.endswith('chromedriver.exe'):
                                with zip_file.open(file) as source, open(chromedriver_path, 'wb') as target:
                                    target.write(source.read())
                                break
                    
                    main_logger.info(f"ChromeDriver downloaded successfully to {chromedriver_path}")
                
                main_logger.info(f"Using ChromeDriver at: {chromedriver_path}")
                service = Service(chromedriver_path)
                
            except Exception as e:
                main_logger.error(f"Failed to download ChromeDriver: {str(e)}")
                # Fallback to bundled ChromeDriver if available
                if getattr(sys, 'frozen', False):
                    base_path = sys._MEIPASS
                else:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                
                chromedriver_path = os.path.join(base_path, "chromedriver.exe")
                
                if not os.path.exists(chromedriver_path):
                    main_logger.error(f"ChromeDriver not found at: {chromedriver_path}")
                    return None
                service = Service(chromedriver_path)

            driver = webdriver.Chrome(options=chrome_options, service=service)

            # Set page load timeout
            driver.set_page_load_timeout(22)

            # Verify driver is working
            driver.get("about:blank")
            if driver.current_url != "about:blank":
                main_logger.error("Failed to verify Chrome driver")
                driver.quit()
                return None

            return driver
        except Exception as e:
            main_logger.error(f"An error occurred while starting Chrome driver: {str(e)}", exc_info=True)
            return None

    def __init__(self, output_callback=None):
        self.driver = None
        self.download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.output_dir = Automation.get_output_dir()
        self.output_callback = output_callback or print

    def emit_output(self, message, msg_type="info"):
        """
        Send output message through callback
        Args:
            message (str): The message to send
            msg_type (str): Type of message ('info', 'success', 'error', 'header', 'status', 'form')
        """
        if self.output_callback:
            self.output_callback(message, msg_type)
        else:
            main_logger.info(message)

    @staticmethod
    def safe_find(driver, by: By, value: str, timeout=5, father_element=None):
        try:
            if father_element:
                return father_element.find_element(by, value)
            else:
                return WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
        except (
            NoSuchElementException,
            TimeoutException,
            StaleElementReferenceException,
        ):
            return None

    def save_page_as_pdf(self, output_pdf_path):
        params = {"landscape": False, "paperWidth": 8.27, "paperHeight": 11.69}
        try:
            data = self.driver.execute_cdp_cmd("Page.printToPDF", params)
            # save the output to a file.
            with open(output_pdf_path, "wb") as file:
                file.write(base64.b64decode(data["data"]))

            return True
        except Exception as e:
            main_logger.error(f"Failed to save PDF: {str(e)}")
            return False

    def move_downloaded_file(self, initial_files, output_folder_path, new_filename):
        try:
            time.sleep(0.5)
            current_files = os.listdir(self.download_dir)

            new_files = []
            for _ in range(5):
                new_files = [
                    f
                    for f in current_files
                    if f not in initial_files
                    and not f.endswith(
                        (
                            ".tmp",
                            ".crdownload",
                            ".part",
                            ".download",
                            ".partial",
                            ".temp",
                            ".incomplete",
                            ".downloading",
                        )
                    )
                ]
                if new_files:
                    break
                time.sleep(1)

            if new_files:
                newest_file = max(
                    new_files,
                    key=lambda f: os.path.getmtime(os.path.join(self.download_dir, f)),
                )
                main_logger.debug(f"new file found {newest_file}")

                source_path = os.path.join(self.download_dir, newest_file)
                # Normalize paths to handle special characters
                output_folder_path = os.path.normpath(output_folder_path)
                target_path = os.path.normpath(os.path.join(output_folder_path, new_filename))

                os.makedirs(output_folder_path, exist_ok=True)
                if os.path.exists(source_path):
                    if os.path.exists(target_path):
                        try:
                            os.remove(target_path)
                        except Exception as e:
                            main_logger.error(f"Failed to remove existing target file: {str(e)}")
                            return False
                else:
                    return None
            else:
                main_logger.error("No new files found after download attempt")
                return None

        except FileNotFoundError as e:
            main_logger.error(f"File not found error: {str(e)}")
            return None
        except PermissionError as e:
            main_logger.error(f"Permission error while moving file: {str(e)}")
            return False
        except Exception as e:
            main_logger.error(f"Unexpected error moving file: {str(e)}")
            return False

    def close_popup_windows(self, original_window):
        try:
            new_handles = [
                handle for handle in self.driver.window_handles if handle != original_window
            ]
            for handle in new_handles:
                self.driver.switch_to.window(handle)
                self.driver.close()
            self.driver.switch_to.window(original_window)
            time.sleep(0.1)  # Small delay to allow window operations to complete
        except Exception as e:
            main_logger.error(f"Error closing popup windows: {str(e)}")
            
            
if __name__ == "__main__":
    automation = Automation()
    automation.driver = Automation.start_chrome_driver(headless=False)



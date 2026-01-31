"""
Browser Automation - Automated login to social media platforms

Uses Selenium WebDriver to control browser and perform automatic logins.
Supports Instagram, Gmail, Twitter, and Facebook.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

logger = logging.getLogger(__name__)


class BrowserAutomation:
    """
    Handles browser automation for social media login
    """
    
    def __init__(self, headless=False):
        """
        Initialize browser automation
        
        Args:
            headless: If True, browser runs in background (no window)
        """
        self.driver = None
        self.headless = headless
        logger.info("Browser Automation initialized")
    
    def _start_browser(self):
        """Start Chrome browser with proper configuration"""
        try:
            # Chrome options
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Disable automation flags (look more human-like)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Disable notifications
            prefs = {"profile.default_content_setting_values.notifications": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Start browser
            logger.info("🌐 Starting Chrome browser...")
            
            # Try using Chrome's built-in ChromeDriver first (Chrome for Testing)
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("✅ Using Chrome's built-in ChromeDriver")
            except Exception as e1:
                logger.info(f"Built-in driver not available: {e1}")
                logger.info("Trying webdriver-manager...")
                try:
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    logger.info("✅ Using downloaded ChromeDriver")
                except Exception as e2:
                    raise Exception(f"Failed to start browser. Built-in: {e1}. Download: {e2}")
            
            self.driver.maximize_window()
            
            logger.info("✅ Browser started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}")
            return False
    
    def login_instagram(self, username: str, password: str) -> bool:
        """
        Automated login to Instagram
        
        Args:
            username: Instagram username
            password: Instagram password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            # Start browser
            if not self._start_browser():
                return False
            
            # Navigate to Instagram
            logger.info("📱 Opening Instagram...")
            self.driver.get("https://www.instagram.com/")
            time.sleep(3)
            
            # Handle cookie consent if it appears
            try:
                cookie_button = self.driver.find_element(
                    By.XPATH, "//button[contains(text(), 'Allow') or contains(text(), 'Accept')]"
                )
                cookie_button.click()
                logger.info("Accepted cookies")
                time.sleep(1)
            except:
                pass  # No cookie dialog
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 20)
            
            # Wait for username field
            logger.info("⏳ Waiting for login form...")
            time.sleep(3)  # Extra wait for page stability
            
            try:
                # Find username field (try multiple selectors)
                username_field = None
                try:
                    username_field = wait.until(
                        EC.presence_of_element_located((By.NAME, "username"))
                    )
                except:
                    # Try alternative selector
                    username_field = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']")
                    ))
                
                if not username_field:
                    raise Exception("Could not find username field")
                
                # Fill username
                logger.info(f"👤 Entering username: {username}")
                username_field.clear()
                username_field.send_keys(username)
                time.sleep(1)
                
                # Find password field
                password_field = self.driver.find_element(By.NAME, "password")
                
                # Fill password
                logger.info("🔑 Entering password...")
                password_field.clear()
                password_field.send_keys(password)
                time.sleep(1)
                
                # Find and click login button
                # Instagram login button can be found by type="submit"
                login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                logger.info("🖱️ Clicking login button...")
                login_button.click()
                
                # Wait for login to process
                logger.info("⏳ Waiting for login to complete...")
                time.sleep(5)
                
                # Check if login succeeded
                current_url = self.driver.current_url
                
                # If we're redirected away from login page, success!
                if "login" not in current_url and "instagram.com" in current_url:
                    logger.info("✅ Login successful!")
                    
                    # Handle "Save Login Info" dialog if it appears
                    try:
                        not_now_button = self.driver.find_element(
                            By.XPATH, "//button[contains(text(), 'Not Now')]"
                        )
                        not_now_button.click()
                        logger.info("Dismissed 'Save Login Info' dialog")
                    except:
                        pass  # Dialog didn't appear
                    
                    # Handle "Turn on Notifications" dialog if it appears
                    try:
                        time.sleep(2)
                        not_now_button = self.driver.find_element(
                            By.XPATH, "//button[contains(text(), 'Not Now')]"
                        )
                        not_now_button.click()
                        logger.info("Dismissed 'Turn on Notifications' dialog")
                    except:
                        pass  # Dialog didn't appear
                    
                    return True
                else:
                    logger.error("❌ Login failed - still on login page")
                    logger.error(f"Current URL: {current_url}")
                    return False
                    
            except TimeoutException:
                logger.error("❌ Timeout waiting for login elements")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during Instagram login: {str(e)}")
            return False
    
    def login_gmail(self, username: str, password: str) -> bool:
        """
        Automated login to Gmail
        
        Args:
            username: Email address
            password: Gmail password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            if not self._start_browser():
                return False
            
            logger.info("📧 Opening Gmail...")
            self.driver.get("https://mail.google.com")
            
            wait = WebDriverWait(self.driver, 15)
            
            # Enter email
            email_field = wait.until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            logger.info(f"📧 Entering email: {username}")
            email_field.send_keys(username)
            
            # Click Next
            next_button = self.driver.find_element(By.ID, "identifierNext")
            next_button.click()
            time.sleep(2)
            
            # Enter password
            password_field = wait.until(
                EC.presence_of_element_located((By.NAME, "Passwd"))
            )
            logger.info("🔑 Entering password...")
            password_field.send_keys(password)
            
            # Click Next
            next_button = self.driver.find_element(By.ID, "passwordNext")
            next_button.click()
            time.sleep(5)
            
            # Check if logged in
            if "mail.google.com" in self.driver.current_url and "signin" not in self.driver.current_url:
                logger.info("✅ Gmail login successful!")
                return True
            else:
                logger.error("❌ Gmail login failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during Gmail login: {str(e)}")
            return False
    
    def login_twitter(self, username: str, password: str) -> bool:
        """
        Automated login to Twitter/X
        
        Args:
            username: Twitter username or email
            password: Twitter password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            if not self._start_browser():
                return False
            
            logger.info("🐦 Opening Twitter/X...")
            self.driver.get("https://twitter.com/i/flow/login")
            
            wait = WebDriverWait(self.driver, 15)
            time.sleep(3)
            
            # Enter username
            username_field = wait.until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            logger.info(f"👤 Entering username: {username}")
            username_field.send_keys(username)
            
            # Click Next
            next_button = self.driver.find_element(
                By.XPATH, "//span[contains(text(), 'Next')]"
            )
            next_button.click()
            time.sleep(2)
            
            # Enter password
            password_field = wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            logger.info("🔑 Entering password...")
            password_field.send_keys(password)
            
            # Click Login
            login_button = self.driver.find_element(
                By.XPATH, "//span[contains(text(), 'Log in')]"
            )
            login_button.click()
            time.sleep(5)
            
            # Check if logged in
            if "home" in self.driver.current_url:
                logger.info("✅ Twitter login successful!")
                return True
            else:
                logger.error("❌ Twitter login failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during Twitter login: {str(e)}")
            return False
    
    def login_github(self, username: str, password: str) -> bool:
        """
        Automated login to GitHub
        
        Args:
            username: GitHub username or email
            password: GitHub password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            if not self._start_browser():
                return False
            
            logger.info("🐙 Opening GitHub...")
            self.driver.get("https://github.com/login")
            
            wait = WebDriverWait(self.driver, 15)
            time.sleep(2)
            
            # Enter username
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "login_field"))
            )
            logger.info(f"👤 Entering username: {username}")
            username_field.clear()
            username_field.send_keys(username)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            logger.info("🔑 Entering password...")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click Sign in
            sign_in_button = self.driver.find_element(By.NAME, "commit")
            logger.info("🖱️ Clicking sign in...")
            sign_in_button.click()
            
            time.sleep(4)
            
            # Check if logged in
            current_url = self.driver.current_url
            if "github.com" in current_url and "login" not in current_url:
                logger.info("✅ GitHub login successful!")
                return True
            else:
                logger.error("❌ GitHub login failed")
                logger.error(f"Current URL: {current_url}")
                # Save screenshot for debugging
                try:
                    screenshot_path = "github_login_error.png"
                    self.driver.save_screenshot(screenshot_path)
                    logger.info(f"📸 Saved error screenshot to {screenshot_path}")
                except:
                    pass
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during GitHub login: {str(e)}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            logger.info("Closing browser...")
            self.driver.quit()
            self.driver = None
            logger.info("Browser closed")
    
    def keep_alive(self):
        """Keep browser window open (don't close automatically)"""
        logger.info("✅ Browser login complete! Window will stay open.")
        logger.info("Close the browser window when you're done.")

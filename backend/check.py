import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import atexit
import logging

logger = logging.getLogger(__name__)

class WebDriverManager:
    """Singleton pattern for WebDriver management to prevent memory leaks"""
    _instance = None
    _driver = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_driver(self):
        if self._driver is None:
            try:
                brave_path = "/usr/bin/brave-browser"
                options = Options()
                options.binary_location = brave_path
                options.add_argument('--headless')  # Run in headless mode for better performance
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920,1080')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-logging')
                options.add_argument('--disable-web-security')
                options.add_argument('--disable-features=VizDisplayCompositor')
                
                self._driver = webdriver.Chrome(options=options)
                self._driver.set_page_load_timeout(30)
                
                # Register cleanup function
                atexit.register(self.cleanup)
                logger.info("WebDriver initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize WebDriver: {e}")
                raise
                
        return self._driver
    
    def cleanup(self):
        if self._driver:
            try:
                self._driver.quit()
                self._driver = None
                logger.info("WebDriver cleaned up successfully")
            except Exception as e:
                logger.error(f"Error during WebDriver cleanup: {e}")

# Create global instance
driver_manager = WebDriverManager()

def check(val):
    """
    Improved check function with better error handling and resource management
    """
    if not val or not val.strip():
        logger.warning("Empty value provided to check function")
        return []
    
    try:
        driver = driver_manager.get_driver()
        val = val.strip()
        
        url = f'https://search.brave.com/search?q=money+control+stock+price+quote+{val}+sentiment&source=web&summary=1&summary_og=a6679b4b51cbf375e6b601'
        
        logger.info(f"Searching for: {val}")
        driver.get(url)
        
        # Use explicit wait with timeout
        wait = WebDriverWait(driver, 30)
        script_tags = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'llm-output'))
        )
        
        logger.info(f"Found {len(script_tags)} elements for {val}")
        return script_tags
        
    except Exception as e:
        logger.error(f"Error in check function for {val}: {e}")
        return []

# Cleanup function for graceful shutdown
def cleanup_driver():
    driver_manager.cleanup()
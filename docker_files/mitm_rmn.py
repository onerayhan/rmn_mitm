from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
import pytz
import threading
import os
import logging
from google.cloud import logging as gcloud_logging
from google.cloud import storage

# Configure Google Cloud Logging
gcloud_logging_client = gcloud_logging.Client()
logger = gcloud_logging_client.logger("selenium-log")

# Read environment variables
DAY_ORDER_IN_CALENDAR = int(os.environ.get('DAY_ORDER_IN_CALENDAR', 15))
MONTH_ORDER_IN_CALENDAR = int(os.environ.get('MONTH_ORDER_IN_CALENDAR', 10))
HOUR = int(os.environ.get('HOUR', 8))
MINUTE = int(os.environ.get('MINUTE', 59))
SECOND = int(os.environ.get('SECOND', 59))
MICROSECOND = int(os.environ.get('MICROSECOND', 750000))
TIP_FORMULAR = os.environ.get('TIP_FORMULAR', '6')
NUME_PASAPORT = os.environ.get('NUME_PASAPORT', 'Akyuz')
PRENUME_PASAPORT = os.environ.get('PRENUME_PASAPORT', 'Huseyin')
LOCUL_NASTERII = os.environ.get('LOCUL_NASTERII', 'Istanbul')
PRENUME_MAMA = os.environ.get('PRENUME_MAMA', 'Safiye')
PRENUME_TATA = os.environ.get('PRENUME_TATA', 'Ahmet')
EMAIL = os.environ.get('EMAIL', 'kivircikhuseyinakyuz@gmail.com')
NUMAR_PASAPORT = os.environ.get('NUMAR_PASAPORT', 'U32117319')
DATA_NASTERII = os.environ.get('DATA_NASTERII', '1980-05-09')
PROXY_HOST = os.environ.get('PROXY_HOST', 'mitmdump')
PROXY_PORT = os.environ.get('PROXY_PORT', '8080')
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'rmn-bucket')
WEBSITE_URL = os.environ.get('WEBSITE_URL', 'http://mitm.it/') 

try: 
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(GCS_BUCKET_NAME)
    logger.log_text(f"Connected to Google Cloud Storage bucket: {GCS_BUCKET_NAME}")
except Exception as e:
    logger.log_text(f"Failed to connect to Google Cloud Storage: {e}", severity="ERROR")




# Function to release the semaphore at 9:00 am Turkey time
semaphore = threading.Semaphore(0)


def release_semaphore_at_spec_time():

    tz = pytz.timezone('Europe/Istanbul')
    now = datetime.datetime.now(tz)
    target_time = now.replace(hour=HOUR, minute=MINUTE, second=SECOND, microsecond=MICROSECOND)
    if now > target_time:
        # If it's already past 9:00 am, set the target to 9:00 am the next day
        target_time += datetime.timedelta(days=1)
    time_to_wait = (target_time - now).total_seconds() - 10
    if time_to_wait > 0:
        time.sleep(time_to_wait)

    # Spin lock for the remaining time
    while datetime.datetime.now(tz) < target_time:
        time.sleep(0.01)  # Check every 100 milliseconds

    semaphore.release()


thread = threading.Thread(target=release_semaphore_at_spec_time)
thread.start()

# Set up mitmproxy
# Set up mitmproxy
proxy = f"{PROXY_HOST}:{PROXY_PORT}"


# Configure Chrome options to use mitmproxy
chrome_options = Options()
chrome_options.add_argument(f"--proxy-server=http://{proxy}")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--ignore-certificate-errors")

# Set SSL key and certificate
chrome_options.add_argument(f"--ssl-client-certificate-file=/etc/ssl/certs/mitmproxy-ca-cert.pem")
# chrome_options.add_argument("--ssl-client-key-passphrase=your_certificate_password")
chrome_options.add_argument("--ignore-ssl-errors=yes")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--allow-insecure-localhost")

try: 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    logger.log_text("Selenium WebDriver started successfully.")
except Exception as e:
    logger.log_text(f"Failed to start Selenium WebDriver: {e}",severity="ERROR")
# Wait for the semaphore to be released
#semaphore.acquire()

start_time = time.time()

try:
    # Open the webpage
    driver.get(WEBSITE_URL)
    logger.log_text("Opened the webpage.")
    html_content = driver.page_source

    # logger.log_text(driver.)
except Exception as e:
    logger.log_text(f"Failed to open the webpage: {e}", severity="ERROR")
# Upload HTML content to Google Cloud Storage
try:
    blob = bucket.blob("page_content.html")
    blob.upload_from_string(html_content, content_type='text/html')
    logger.log_text(f"HTML content uploaded to Google Cloud Storage bucket: {GCS_BUCKET_NAME} as page_content.html")
except Exception as e:
    logger.log_text(f"Failed to upload HTML content to Google Cloud Storage: {e}", severity="ERROR")

# Bypass the security warning page
try:
    details_button = driver.find_element(By.ID, "details-button")
    driver.execute_script("arguments[0].click();", details_button)
    proceed_link = driver.find_element(By.ID, "proceed-link")
    driver.execute_script("arguments[0].click();", proceed_link)
    logger.log_text("Bypassed the security warning page.")
except Exception as e:
    logger.log_text(f"Failed to bypass the security warning page: {e}",severity="WARNING")
    pass

# Wait for the page to load completely
time.sleep(2)

element = driver.find_element(By.ID, "gdpr")
driver.execute_script("arguments[0].click();", element)

select_element = Select(driver.find_element(By.ID, "tip_formular"))
select_element.select_by_value(TIP_FORMULAR)


# Fill out the input fields
driver.find_element(By.ID, "nume_pasaport").send_keys(NUME_PASAPORT)
driver.find_element(By.ID, "prenume_pasaport").send_keys(PRENUME_PASAPORT)
driver.find_element(By.ID, "locul_nasterii").send_keys(LOCUL_NASTERII)
driver.find_element(By.ID, "prenume_mama").send_keys(PRENUME_MAMA)
driver.find_element(By.ID, "prenume_tata").send_keys(PRENUME_TATA)
driver.find_element(By.ID, "email").send_keys(EMAIL)
driver.find_element(By.ID, "numar_pasaport").send_keys(NUMAR_PASAPORT)
driver.find_element(By.ID, "data_nasterii").send_keys(DATA_NASTERII)
'''
driver.find_element(By.ID, "nume_pasaport").send_keys("Akarsd")
driver.find_element(By.ID, "prenume_pasaport").send_keys("Huesdhg")
driver.find_element(By.ID, "locul_nasterii").send_keys("Isdst")
driver.find_element(By.ID, "prenume_mama").send_keys("Safi")
driver.find_element(By.ID, "prenume_tata").send_keys("Ahmas")
driver.find_element(By.ID, "email").send_keys("kivsyuz@gmail.com")
driver.find_element(By.ID, "numar_pasaport").send_keys("U345319")
driver.find_element(By.ID, "data_nasterii").send_keys("1981-06-09")
'''

'''
driver.execute_script("""
    var customDelayElement = document.getElementById('custom_delay');
    if (customDelayElement) {
        customDelayElement.parentNode.removeChild(customDelayElement);
    }
    var transmitButton = document.getElementById('transmite');
    if (transmitButton) {
        transmitButton.removeAttribute('disabled');
    }
""") '''

time.sleep(10)

datepicker_switch = driver.find_element(By.CLASS_NAME, 'datepicker-switch')
driver.execute_script("arguments[0].click();", datepicker_switch)

time.sleep(1)
months = driver.find_elements(By.CLASS_NAME, 'month')
month = months[MONTH_ORDER_IN_CALENDAR]
driver.execute_script("arguments[0].click();", month)
time.sleep(10)


days = driver.find_elements(By.CLASS_NAME, 'day')
day = days[DAY_ORDER_IN_CALENDAR]
driver.execute_script("arguments[0].click();", day)


time.sleep(10)
transmit_button = driver.find_element(By.ID, "transmite")
semaphore.acquire()
driver.execute_script("arguments[0].click();", transmit_button)

end_time = time.time()
elapsed_time = end_time - start_time
#print(f"Elapsed time: {elapsed_time} seconds")

time.sleep(5)
driver.save_screenshot("form_filled5.png")

driver.quit()

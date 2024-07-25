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

DAY_ORDER_IN_CALENDAR = 15
MONTH_ORDER_IN_CALENDAR = 10
# Function to release the semaphore at 9:00 am Turkey time
semaphore = threading.Semaphore(0)


def release_semaphore_at_9am():

    tz = pytz.timezone('Europe/Istanbul')
    now = datetime.datetime.now(tz)
    target_time = now.replace(hour=8, minute=59, second=59, microsecond=750000)
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


thread = threading.Thread(target=release_semaphore_at_9am)
thread.start()

# Set up mitmproxy
proxy = "localhost:8080"

# Configure Chrome options to use mitmproxy
chrome_options = Options()
chrome_options.add_argument(f"--proxy-server=http://{proxy}")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Wait for the semaphore to be released
#semaphore.acquire()

start_time = time.time()

# Open the webpage
driver.get("https://programarecetatenie.eu/")

# Bypass the security warning page
try:
    details_button = driver.find_element(By.ID, "details-button")
    driver.execute_script("arguments[0].click();", details_button)
    proceed_link = driver.find_element(By.ID, "proceed-link")
    driver.execute_script("arguments[0].click();", proceed_link)
except:
    pass

# Wait for the page to load completely
time.sleep(1)

element = driver.find_element(By.ID, "gdpr")
driver.execute_script("arguments[0].click();", element)

select_element = Select(driver.find_element(By.ID, "tip_formular"))
select_element.select_by_value("6")


# Fill out the input fields
driver.find_element(By.ID, "nume_pasaport").send_keys("Akyuz")
driver.find_element(By.ID, "prenume_pasaport").send_keys("Huseyin")
driver.find_element(By.ID, "locul_nasterii").send_keys("Istanbul")
driver.find_element(By.ID, "prenume_mama").send_keys("Safiye")
driver.find_element(By.ID, "prenume_tata").send_keys("Ahmet")
driver.find_element(By.ID, "email").send_keys("kivircikhuseyinakyuz@gmail.com")
driver.find_element(By.ID, "numar_pasaport").send_keys("U32117319")
driver.find_element(By.ID, "data_nasterii").send_keys("1980-05-09")
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

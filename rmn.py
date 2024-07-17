from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import time
import datetime
import pytz
import threading


DAY_ORDER_IN_CALENDAR = 16
MONTH_ORDER_IN_CALENDAR = 10
# Semaphore to control the execution
semaphore = threading.Semaphore(0)


# Function to release the semaphore at 9:00 am Turkey time
def release_semaphore_at_9am():
    tz = pytz.timezone('Europe/Istanbul')
    now = datetime.datetime.now(tz)
    target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now > target_time:
        # If it's already past 9:00 am, set the target to 9:00 am the next day
        target_time += datetime.timedelta(days=1)
    time_to_wait = (target_time - now).total_seconds() - 20
    if time_to_wait > 0:
        time.sleep(time_to_wait)

    # Spin lock for the remaining time
    while datetime.datetime.now(tz) < target_time:
        time.sleep(0.1)  # Check every 100 milliseconds

    semaphore.release()


# Start a thread to release the semaphore
thread = threading.Thread(target=release_semaphore_at_9am)
thread.start()

# Start the timer
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
# Wait for the semaphore to be released
#semaphore.acquire()



start_time = time.time()

# Open the webpage
driver.get("https://programarecetatenie.eu/")
# Select the option from the dropdown
#driver.find_element(By.ID, "gdpr").click()
# Locate the element using its ID

element = driver.find_element(By.ID, "gdpr")
driver.execute_script("arguments[0].click();", element)


select_element = Select(driver.find_element(By.ID, "tip_formular"))
select_element.select_by_value("4")

# Fill out the input fields
driver.find_element(By.ID, "nume_pasaport").send_keys("Vuran")
driver.find_element(By.ID, "prenume_pasaport").send_keys("Kivanc")
driver.find_element(By.ID, "locul_nasterii").send_keys("Babaeski")
driver.find_element(By.ID, "prenume_mama").send_keys("Aliye")
driver.find_element(By.ID, "prenume_tata").send_keys("Nizamettin")
driver.find_element(By.ID, "email").send_keys("ozkutpaslanmaz42@gmail.com")
driver.find_element(By.ID, "numar_pasaport").send_keys("U14532425")
driver.find_element(By.ID, "data_nasterii").send_keys("1979-01-22")

# Wait for the spinner to appear and disappear
#spinner = driver.find_element(By.ID, "custom_delay")
#WebDriverWait(driver, 20).until(EC.visibility_of(spinner))
#WebDriverWait(driver, 20).until(EC.invisibility_of_element(spinner))
driver.execute_script("""
    // Delete the HTML element
    var customDelayElement = document.getElementById('custom_delay');
    if (customDelayElement) {
        customDelayElement.parentNode.removeChild(customDelayElement);
    }

    // Enable the button
    var transmitButton = document.getElementById('transmite');
    if (transmitButton) {
        transmitButton.removeAttribute('disabled');
    }
""")

datepicker_switch = driver.find_element(By.CLASS_NAME, 'datepicker-switch')
driver.execute_script("arguments[0].click();", datepicker_switch)

# Select the month
months = driver.find_elements(By.CLASS_NAME, 'month')
month = months[MONTH_ORDER_IN_CALENDAR]
print(month.id)


# Select the day
days = driver.find_elements(By.CLASS_NAME, 'day')
# counter = 0
day = days[DAY_ORDER_IN_CALENDAR]
driver.execute_script("arguments[0].click();", day)

# Click the GDPR checkbox


# Wait until the spinner button is invisible before clicking the submit button
#spinner_button = driver.find_element(By.ID, "spinner_button")
#WebDriverWait(driver, 20).until(EC.invisibility_of_element(spinner_button))
driver.save_screenshot("form_filled2.png")
# Click the submit button
#driver.find_element(By.ID, "transmite").click()
transmit_button = driver.find_element(By.ID, "transmite")
driver.execute_script("arguments[0].click();", transmit_button)


# Stop the timer
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")
time.sleep(5)
# Close the browser
# driver.quit()

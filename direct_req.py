import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Setup Selenium to get the reCAPTCHA token
def get_recaptcha_token1(site_key, url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)

    token_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "recaptcha-token"))
    )
    #recaptcha_token = token_element.get_attribute("value")
    # Use JavaScript to get the value of the hidden input element
    recaptcha_token = driver.execute_script("return arguments[0].value;", token_element)

    driver.quit()
    return recaptcha_token
# Setup Selenium to get the reCAPTCHA token
def get_recaptcha_token(site_key, url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

    try:
        # Wait for the reCAPTCHA to be ready
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'div.g-recaptcha[data-sitekey="{site_key}"]'))
        )

        # Trigger the invisible reCAPTCHA
        driver.execute_script(f"""
            grecaptcha.execute('{site_key}', {{action: 'homepage'}}).then(function(token) {{
                document.getElementById('g-recaptcha-response').value = token;
            }});
        """)

        # Wait for the token to be set
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element_value((By.ID, "g-recaptcha-response"), "token")
        )

        # Get the value of the hidden input element
        recaptcha_token = driver.execute_script("return document.getElementById('g-recaptcha-response').value;")
    except Exception as e:
        print(f"Error obtaining reCAPTCHA token: {e}")
        recaptcha_token = None
    finally:
        driver.quit()

    return recaptcha_token
# URL and site key for reCAPTCHA
url = "https://programarecetatenie.eu/"
site_key = "6LcnPeckAAAAABfTS9aArfjlSyv7h45waYSB_LwT"

# Get the reCAPTCHA token
recaptcha_token = get_recaptcha_token(site_key, url)

# Form data to be sent
data = {
    "nume_pasaport": "Vuran",
    "prenume_pasaport": "Kıvanç",
    "locul_nasterii": "Babaeski",
    "prenume_mama": "Aliye",
    "prenume_tata": "Nizamettin",
    "email": "ozkutpaslanmaz39@gmail.com",
    "numar_pasaport": "U14534225",
    "data_nasterii": "1979-01-22",
    "tip_formular": "4",
    "azi": "2024-07",  # Replace this with the current year-month
    "data_programarii": "2024-11-12",  # Desired appointment date
    "g-recaptcha-response": recaptcha_token
}

# Headers for the request
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# Make the POST request to the server
response = requests.post("https://programarecetatenie.eu/status_zile", data=data, headers=headers)

# Print the response from the server
print(response.text)

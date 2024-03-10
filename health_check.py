from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import time
from bs4 import BeautifulSoup
import json 
from playsound import playsound
from datetime import datetime

def create_driver():
    chrome_options = Options()
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def start_new_booking(driver):
    driver.get('https://bmvs.onlineappointmentscheduling.net.au/oasis/Location.aspx')
    
    wait = WebDriverWait(driver, 10)
    start_booking_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Start a new booking']")))
    start_booking_button.click()
    new_individual_booking_xpath = "/html/body/form/div[3]/div[2]/div[1]/div[2]/div[1]/button"

    
    new_individual_booking_button = wait.until(EC.element_to_be_clickable((By.XPATH, new_individual_booking_xpath)))
    new_individual_booking_button.click()

    time.sleep(10)

    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')

    available_slots = {}
    locations_of_interest = ['Sydney', 'Parramatta', 'Bankstown ', 'Corrimal', 'Newcastle']

    for location in locations_of_interest:
        location_info = soup.find('label', class_='tdlocNameTitle', string=location)
        if location_info:
            parent_row = location_info.find_parent('tr')
            if parent_row:
                availability_info = parent_row.find('td', class_='tdloc_availability').get_text(strip=True)
                available_slots[location] = availability_info
    return available_slots
   
def is_within_30_days(date_str):
    try:
        slot_date = datetime.strptime(date_str, "%A %d/%m/%Y%H:%M %p")
        # print(slot_date)
        current_date = datetime.now()
        difference = slot_date - current_date
        print(f"===============> {difference.days}")
        return difference.days <= 60
    except ValueError as e:
        print(e)
        return False 
    
try:
    while True:
        try:
            driver = create_driver() 
            available_slots = start_new_booking(driver)
            for location, availability in available_slots.items():
                print(f"{location}: {availability}")
                if "No available slot" not in availability:
                    if is_within_30_days(availability):
                        print("Playing sound for slot within 30 days...")
                        playsound('song.mp4')
                        time.sleep(6000000)
                        break 
                else:
                    driver.quit()
            time.sleep(20)
        except WebDriverException as e:
            print(f"WebDriver error occurred: {e}")
        finally:
            if driver:
                driver.quit()
except KeyboardInterrupt:
    print("Loop has been manually terminated.")
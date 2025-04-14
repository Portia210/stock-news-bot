import requests
from utils.automation_utils import Automation
from selenium.webdriver.common.by import By
import time


base_url = "https://www.investing.com/economic-calendar/"   


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    # cookie
    "cookie": "ASP.NET_SessionId=pe2eentrvp555xz1ealry2iu; TEServer=TEIIS; cal-timezone-offset=180; _ga=GA1.1.323407407.1744019522; _ga_SZ14JCTXWQ=GS1.1.1744019522.1.1.1744019523.59.0.0; FCNEC=%5B%5B%22AKsRol8WFIXX1AArLdcouhD_e6ycagQmdEV2b6uQUV8SJI9hZVuVqtIPUT35F5dmhR_D0Bze95AzmSB1UiaRkibf3Tmu-ie0uc9m-5kYW-8_B3ieYF0Mj_MP-FDGOHK8Dwqe1cPtnoddWo4rUpDGQUvPFqMoeMDvoA%3D%3D%22%5D%5D"
}

def main():
    driver = Automation.start_chrome_driver(headless=False)
    driver.get(base_url)
    time.sleep(1)
    calendar_data = Automation.safe_find(driver, By.ID, "economicCalendarData")
    print(calendar_data)
    driver.quit()


if __name__ == "__main__":
    main()

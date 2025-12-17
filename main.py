import math
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import yfinance as yf
# from pprint import pprint
import csv
import time


def scrape_yahoo_fin_stocks():
    base_url = "https://finance.yahoo.com/markets/stocks"
    sort_condition = "losers"

    cats = [
        "Ticker", "Sector",
        "Current Price", "1D Change",
        "5D Change", "1M Change", "6M Change",
        "1Y Change", "5Y Change", "All Change"
    ]

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
    }



    # List to store the scraped data
    data = []


    def scrape_stock_details(stock_url):
        response = requests.get(stock_url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")

        #print(soup.prettify()[:1000])

        stock_name = soup.find("h1", class_="yf-4vbjci")
        stock_name = stock_name.text.strip() if stock_name else "N/A"

        #sector = soup.find_all("a", class_="subtle-link fin-size-medium ellipsis yf-1i440lo")
        sector = soup.find("span", class_="titleInfo yf-1d08kze")
        sector = sector.text.strip() if sector else "N/A"
        #print(sector)

        #industry = sector[1].text.strip()
        #sector = sector[0].text.strip() if sector else "N/A"

        price = soup.find_all("span", class_="yf-ipw1h0 base")
        price = price[0].text.strip() if price else "N/A"

        # Gets the percent change in price over different periods
        if sort_condition == "losers":
            #odc = soup.find_all("span", class_="txt-negative yf-ipw1h0 base")
            odc = soup.find_all("span", class_="txt-negative change yf-1c9i0iv")
        elif sort_condition == "gainers":
            odc = soup.find_all("span", class_="txt-positive yf-ipw1h0 base")
        else:
            print("unknown sort condition")
            return 0
        odc = odc[0].text.strip() if odc else "N/A"
        #print(odc)

        details = soup.find_all("h3", class_="title yf-17ug8v2")

        fdc = details[0].text.strip() if len(details) > 0 else "N/A"
        omc = details[1].text.strip() if len(details) > 1 else "N/A"
        smc = details[2].text.strip() if len(details) > 2 else "N/A"
        oyc = details[4].text.strip() if len(details) > 4 else "N/A"
        fyc = details[5].text.strip() if len(details) > 5 else "N/A"
        atc = details[6].text.strip() if len(details) > 6 else "N/A"

        return [
            stock_name, sector, price, odc, fdc, omc,
            smc, oyc, fyc, atc
        ]

    # Loop through the top stocks based on the sort_condition
    def scrape_stock_list(page_url):
        response = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        #print(soup.prettify()[:1000])
        id_list = soup.find_all("a", class_="ticker medium [&_.symbol]:tw-text-md hover noPadding yf-90gdtp")


        if not id_list:
            print("No dataset links found")
            return

        # print(id_list)

        for dataset in id_list:
            stock_link = f"https://finance.yahoo.com" + dataset["href"]
            print(f"Scraping details for {dataset.text.strip()}...")
            dataset_details = scrape_stock_details(stock_link)
            if dataset_details[0] == "N/A":
                continue
            data.append(dataset_details)
            time.sleep(1)


    # Loop through the top stocks based on the sort_condition
    page_url = f"https://finance.yahoo.com/markets/stocks/{sort_condition}"
    print(page_url)
    #print(f"Scraping page: {page_url}")
    #initial_data_count = len(data)
    scrape_stock_list(page_url)

    with open("yahoofin_data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(cats)
        writer.writerows(data)
def scrape_msn_money_stocks():
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
    except ValueError:
        print("WebDriverManager failed. Trying to run ChromeDriver from path.")
        print("If this fails, download ChromeDriver and place it in your script's directory.")
        driver = webdriver.Chrome()

    wait = WebDriverWait(driver, 15)

    print("Scraping complete. Data saved to 'yahoofin_data.csv'.")
    sort_condition = "Losers"
    sort_condition_temp = input("What condition would you like to sort the data by?")

    if sort_condition_temp.lower() == "losers" or sort_condition_temp.lower() == "gainers":  # can add another 'or' if they want full shabang data or just ticker name
        sort_condition = sort_condition_temp.capitalize()
    else:
        print("Sort condition not recognized, defaulting to losers")

    driver.get(f"https://int1.msn.com/en-us/money/markets?tab=Top{sort_condition}")  # Capital L Loser

    time.sleep(3)

    stock_list = driver.find_elements(By.CLASS_NAME, "quoteTitle-DS-EntryPoint1-4")
    facts_list = ["Ticker", "Price", "Previous Close",
                  "Average Volume", "Shares Outstanding", "EPS (TTM)",
                  "P/E (TTM)", "Fwd Dividend (% Yield)", "Ex-Dividend Date"]
    facts_val_list = []

    count = math.inf
    while count > len(stock_list):
        count = int(input(f"How many stocks would you like to scrape? Max is {len(stock_list)}"))
        if count > len(stock_list):
            print("Input exceeds maximum. Please try again.")

    #print(len(stock_list))
    for stock in stock_list:
        # Stop early
        if stock_list.index(stock) == count:
            break

        # Accounts for bug where last list item isn't actually shown
        if stock.text == stock_list[len(stock_list)-1].text:
            break
        stock.click()
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", stock)
        time.sleep(1)
        symbol = driver.find_element(By.CLASS_NAME, "symbolWithBtn-DS-EntryPoint1-1").text
        print(f"Scraping {stock.text}")
        price = driver.find_element(By.CSS_SELECTOR, ".mainPrice").text

        facts_elements = driver.find_elements(By.CLASS_NAME, "factsRowKey-DS-EntryPoint1-1")
        facts_val_elements = driver.find_elements(By.CLASS_NAME, "factsRowValue-DS-EntryPoint1-1")

        facts_val_list.append([symbol, price])

        for n in range(len(facts_elements)):
            facts_val_list[len(facts_val_list)-1].append(facts_val_elements[n].text)

        #  For testing/displaying data
        # print(f"- {symbol}: {price}")
        # for n in range(len(facts_elements)):
        #     if facts_val_elements[n].text != "-":
        #         print(f"   {facts_elements[n].text}: {facts_val_elements[n].text}")
        #for n in range(0, len(facts_list), 2):
        #    print(f"    {facts_list[n].text}: {facts_list[n+1].text}")


    driver.quit()

    with open("msn_money_data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(facts_list)
        writer.writerows(facts_val_list)

    print("Scraping complete. Data saved to 'msn_money_data.csv'.")


if __name__ == "__main__":
    scrape_msn_money()

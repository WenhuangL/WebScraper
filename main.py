import requests
from bs4 import BeautifulSoup
import csv
import time


def scrape_msn_money():
    base_url = "https://finance.yahoo.com/markets/stocks"
    sort_condition = "gainers"

    cats = [
        "Ticker", "Sector", "Industry",
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

        soup = BeautifulSoup(response.text, 'html.parser')

        #print(soup.prettify()[:1000])

        stock_name = soup.find('h1', class_='yf-4vbjci')
        stock_name = stock_name.text.strip() if stock_name else "N/A"

        #sector = soup.find_all('a', class_='subtle-link fin-size-medium ellipsis yf-1i440lo')
        sector = soup.find('span', class_='titleInfo yf-1d08kze')
        sector = sector.text.strip() if sector else "N/A"
        print(sector)

        #industry = sector[1].text.strip()
        #sector = sector[0].text.strip() if sector else "N/A"

        price = soup.find_all('span', class_='yf-ipw1h0 base')
        price = price[2].text.strip() if price else "N/A"

        # Gets the percent change in price over different periods
        odc = soup.find_all('span', class_='txt-positive yf-ipw1h0 base')
        odc = odc[1].text.strip() if odc else "N/A"

        details = soup.find_all('h3', class_='title yf-17ug8v2')

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

    """
    def scrape_stock_list(page_url):
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        dataset_list = soup.find_all(
            'span', class_='quoteView-DS-EntryPoint1-2 hoverIcon ')
        
        soup = BeautifulSoup(response.text, 'html.parser')


        dataset_list = soup.find_all(
            'a', class_='link-hover link text-xl font-semibold')


        if not dataset_list:
            print("No dataset links found")
            return


        for dataset in dataset_list:
            dataset_link = "https://archive.ics.uci.edu" + dataset['href']
            print(f"Scraping details for {dataset.text.strip()}...")
            dataset_details = scrape_dataset_details(dataset_link)
            data.append(dataset_details)"""


    # Loop through the top stocks based on the sort_condition
    def scrape_stock_list(page_url):
        response = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        #print(soup.prettify()[:1000])
        id_list = soup.find_all('a', class_='ticker medium [&_.symbol]:tw-text-md hover noPadding yf-90gdtp')


        if not id_list:
            print("No dataset links found")
            return

        # print(id_list)

        for dataset in id_list:
            stock_link = f"https://finance.yahoo.com" + dataset['href']
            print(f"Scraping details for {dataset.text.strip()}...")
            dataset_details = scrape_stock_details(stock_link)
            data.append(dataset_details)
            time.sleep(1)


    # Loop through the top stocks based on the sort_condition
    page_url = f"https://finance.yahoo.com/markets/stocks/{sort_condition}"
    print(page_url)
    #print(f"Scraping page: {page_url}")
    #initial_data_count = len(data)
    scrape_stock_list(page_url)

    with open('msn_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

    print("Scraping complete. Data saved to 'yahoofin_data.csv'.")


if __name__ == '__main__':
    scrape_msn_money()

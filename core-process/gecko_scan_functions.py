# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import gecko_scan_libraries as gsl


def main1(path):

    gsl.notice_start("Extract All Cryptocurrencies")

    """
    This try-except block will:
        1. Send a request to the given url
        2. Decide the total number of pages
        3. Store the urls of all pages into a list
    """
    try:
        response = gsl.requests.get("https://www.coingecko.com/", headers=gsl.headers)
        html = response.content
        soup = gsl.bs(html, "html.parser").find_all("li", class_="page-item")

        total_pages = int([obj.get_text() for obj in soup][-2])
        pages = [gsl.base_url]
        for i in range(2, total_pages + 1):
            pages.append(f"{gsl.base_url}?page={str(i)}")
        print(gsl.Fore.WHITE + "Successfully extracted URLs.")

    except:
        gsl.error_url_timeout()

    """
    This try-except block will:
        1. Create an empty dataframe to store data
        2. Send a request to each url in the given list
        3. Transform the obtained html into a sub dataframe
        4. Append each sub dataframe to the main dataframe
        5. Clean the main dataframe
    """
    try:
        print("")
        reset_threshold, df_clean = 0, gsl.pd.DataFrame(
            columns=["Symbol", "Name", "Price", "Change1h", "Change24h", "Change7d", "Volume24h", "MarketCap"])

        for url in pages:
            response = gsl.requests.get(url, headers=gsl.headers)
            html = response.content
            soup = gsl.bs(html, "html.parser")
            soup = soup.find("div", class_="coingecko-table")
            df_page = gsl.extract_page(soup)
            df_clean = gsl.pd.concat([df_clean, df_page], axis=0, ignore_index=True)
            print(gsl.Fore.WHITE, "- Extracting information...")
            gsl.time.sleep(0.5)

            reset_threshold += 1
            if reset_threshold > 25:
                gsl.notice_wait_20()
                reset_threshold = 0
                gsl.time.sleep(20)

        df_clean = gsl.trim_dataframe(df_clean)

        print("")
        print(gsl.Fore.GREEN + "All data ready.")

    except:
        gsl.error_data_timeout()

    """
    This try-except block will:
        1. Create a name for extracted data based on current time
        1. Save extracted data to the given path
    """
    try:
        output_path = path
        output_name = f"all-crypto-{gsl.get_datetime()}.csv"
        df_clean.to_csv(gsl.os.path.join(output_path, output_name))
        gsl.notice_save_success()

    except:
        gsl.error_save_failed()


def main2(path):

    gsl.notice_start("Extract by Category")

    """
    This try-except block will:
        1. Send a request to the given url
        2. Get the name (href) of each category
        3. Store the urls of each category into a list
    """
    try:
        response = gsl.requests.get("https://www.coingecko.com/en/categories", headers=gsl.headers)
        html = response.content
        soup = gsl.bs(html, "html.parser").find("tbody").find_all("a")

        categories_url = []
        for link in soup:
            href = str(link.get("href"))
            if "categories" in href and "ecosystem" not in href:
                categories_url.append(gsl.base_url + href)
                categories_url = list(dict.fromkeys(categories_url))
        print(gsl.Fore.WHITE + "Successfully extracted URLs.")

    except:
        gsl.error_url_timeout()

    """
    This try-except block will:
        1. Create a dictionary to store data in name-dataframe pairs
        2. Send a request to each cateogory url in the given list
        3. Extract a dataframe for each category
        4. Clean the extracted dataframe
        5. Store the cleaned dataframe in the dictionary
    """
    try:
        print("")
        data_dictionary, reset_threshold = {}, 0

        for url in categories_url:
            category = gsl.get_category_name(url)
            num = gsl.get_num_of_pages(gsl.headers, url)
            pages = gsl.get_page_list(num, url)
            data = gsl.extract_dataframe(gsl.headers, pages)
            data = gsl.trim_dataframe(data)
            data_dictionary[category] = data
            print(gsl.Fore.WHITE, f"- Successfully extracted data for {category}")

            reset_threshold += num
            if reset_threshold > 25:
                gsl.notice_wait_20()
                reset_threshold = 0
                gsl.time.sleep(20)

        print("")
        print(gsl.Fore.GREEN + "All data ready.")

    except:
        gsl.error_data_timeout()

    """
    This try-except block will:
        1. Create a name for extracted data from each category
        1. Save extracted data to the given path
    """
    try:
        output_path = path
        for category, dataframe in data_dictionary.items():
            output_name = f"{category}-{gsl.get_datetime()}.csv"
            dataframe.to_csv(gsl.os.path.join(output_path, output_name))
        gsl.notice_save_success()

    except:
        gsl.error_save_failed()


def main3(path):

    gsl.notice_start("Extract Historical Database")  

    """
    This try-except block will:
        1. Create a list of urls that directs to the database
        2. Seperate the full list into batches to prevent stack overflow
    """
    try:
        url_list = [f"https://www.coingecko.com/price_charts/export/{str(i+1)}/usd.csv" for i in range(32000)]
        print(gsl.Fore.WHITE + f"{len(url_list)} URLs has been loaded.")

        batch_size = 1000
        batch_list = []
        for i in range(0, len(url_list), batch_size):
            batch_list.append(url_list[i:i + batch_size])
        print(gsl.Fore.WHITE + f"{len(batch_list)} batches has been created.")
    except:
        gsl.error_url_timeout()

    """
    This try-except block will:
        1. Iterate through each batch in the given list
        1. Recursively download the database for each batch
    """
    try:
        print("")
        output_path = path
        for url_list in batch_list:
            gsl.recursive_download(url_list, output_path)
        print("")
        print(gsl.Fore.GREEN + "All data ready.")
        gsl.notice_save_success()

    except:
        gsl.error_save_failed()

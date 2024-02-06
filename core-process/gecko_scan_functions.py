# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import gecko_scan_libraries as gsl


def main1(driver, path):

    gsl.notice_start("Extract All Cryptocurrencies")

    """
    This try-except block will:
        1. Send a request to the given url
        2. Decide the total number of pages
        3. Store the urls of all pages into a list
    """
    try:
        driver.get("https://www.coingecko.com/")
        html = driver.page_source
        soup = gsl.bs(html, "html.parser").find_all("a", class_="tw-cursor-pointer tw-relative tw-inline-flex tw-items-center tw-rounded-lg tw-px-4 tw-py-1.5 tw-text-sm tw-font-semibold !tw-text-gray-900 hover:tw-bg-gray-50 dark:!tw-text-moon-50 dark:hover:tw-bg-moon-700")

        total_pages = int([obj.get_text() for obj in soup][-1])
        pages = [gsl.base_url]
        for i in range(2, total_pages + 1):
            pages.append(f"{gsl.base_url}?page={str(i)}")

        gsl.notice_url_success(len(pages))

    except:
        gsl.error_url_timeout()

    """
    This try-except block will:
        1. Extract a dataframe for all cryptocurrencies
        2. Clean the dataframe
    """
    try:
        df, threshold = gsl.extract_dataframe(driver, pages, 0, True)
        df = gsl.trim_dataframe(df)

        gsl.info_data_ready()

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
        df.to_csv(gsl.os.path.join(output_path, output_name))
        
        gsl.notice_save_success()

    except:
        gsl.error_save_failed()


def main2(driver, path):

    gsl.notice_start("Extract by Category")

    """
    This try-except block will:
        1. Send a request to the given url
        2. Get the name (href) of each category
        3. Store the urls of each category into a list
    """
    try:
        driver.get("https://www.coingecko.com/en/categories")
        html = driver.page_source
        soup = gsl.bs(html, "html.parser").find("tbody").find_all("a")

        categories_url = []
        for link in soup:
            href = str(link.get("href"))
            if "categories" in href and "ecosystem" not in href:
                categories_url.append(gsl.base_url + href)
                categories_url = list(dict.fromkeys(categories_url))

        gsl.notice_url_success(len(categories_url))

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
        data_dictionary, threshold = {}, 0
        for url in categories_url:
            category = gsl.get_category_name(url)
            num = gsl.get_num_of_pages(driver, url)
            pages = gsl.get_page_list(num, url)

            df, threshold = gsl.extract_dataframe(driver, pages, threshold, False)
            df = gsl.trim_dataframe(df)
            data_dictionary[category] = df
            gsl.info_category(category)

        gsl.info_data_ready()

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


def main3(driver, path):

    gsl.notice_start("Extract Historical Database")

    """
    This try-except block will:
        1. Create a list of urls that directs to the database
        2. Seperate the full list into batches to prevent stack overflow
    """
    try:
        url_list = [f"https://www.coingecko.com/price_charts/export/{str(i+1)}/usd.csv" for i in range(32000)]
        batch_size = 1000
        batch_list = []
        for i in range(0, len(url_list), batch_size):
            batch_list.append(url_list[i:i + batch_size])

        gsl.notice_batch_size(len(batch_list))

    except:
        gsl.error_url_timeout()

    """
    This try-except block will:
        1. Iterate through each batch in the given list
        1. Recursively download the database for each batch
    """
    try:
        output_path = path
        for url_list in batch_list:
            gsl.recursive_download(driver, url_list, output_path)
            
        gsl.info_data_ready()
        gsl.notice_save_success()

    except:
        gsl.error_save_failed()


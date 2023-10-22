# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import gecko_scan_libraries as gsl


def main(path):

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

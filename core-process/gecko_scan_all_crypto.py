# -*- coding: utf-8 -*-
"""
@author: chengmarc
@github: https://github.com/chengmarc

"""
import gecko_scan_libraries as gsl


def main(path):

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

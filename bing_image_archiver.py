import datetime
import os
import pickle
import sys
import time
import urllib
import utils

from iorise_image_extractor import extract_all_image_urls


def update_image_library(download_location):
    """ Function used to update the specified location with all the new images posted on the iorise blog. It uses the
    last_date_scanned.pickle as a log file. """

    # Get current date
    current_date = datetime.date.today()

    # Get last date scanned
    log_file_location = utils.get_log_file_path(download_location)
    last_date_scanned = datetime.date(2012, 11, 25)
    try:
        with open(log_file_location, 'rb') as handle:
            last_date_scanned = pickle.load(handle)
    except IOError:
        pass

    # Download images with dates
    download_images(last_date_scanned, current_date, download_location)

    # Save last date scanned
    with open(log_file_location, 'wb') as handle:
        pickle.dump(current_date, handle)


def download_images(from_date, to_date, download_location):
    """ Function downloading to the specified folder all bing images published on the iorise blog between the
    specified dates. """

    current_date = from_date

    log_file_location = utils.get_log_file_path(download_location)

    while current_date <= to_date:

        image_urls = extract_all_image_urls(current_date)

        print(str(current_date) + ": " + str(len(image_urls)))

        for image_url in image_urls:

            filename = utils.extract_filename_from_url(image_url)
            full_filename = os.path.join(download_location, filename)

            if not os.path.isfile(full_filename):
                urllib.urlretrieve(image_url, full_filename)
                time.sleep(1)

        with open(log_file_location, 'wb') as handle:
            pickle.dump(current_date, handle)

        current_date += datetime.timedelta(1)



if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Wrong number of arguments. Usage: python bing_image_downloader.py destination_folder")
        quit()

    path = sys.argv[1]

    if not os.path.isdir(path):
        print("Specified destination is not a valid folder.")
        quit()

    update_image_library(path)

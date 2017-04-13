import datetime
import os
import pickle
import sys
import time
import urllib.request
import utils
import logging
from multiprocessing.dummy import Pool

from iorise_image_extractor import extract_all_image_urls
from duplicate_remover import remove_duplicate_images


def update_image_library(download_location):
    """ Function used to update the specified location with all the new images posted on the iorise blog. It uses the
    last_date_scanned.pickle as a log file. """

    # Get current date
    current_date = datetime.date.today()

    # Get last date scanned
    log_file_location = utils.get_log_file_path(download_location)
    last_date_scanned = datetime.date(2017, 1, 1)
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

    remove_duplicate_images(download_location, (1920, 1200))


def download_images(from_date, to_date, base_download_location):
    """ Function downloading to the specified folder all bing images published on the iorise blog between the
    specified dates. """

    current_date = from_date

    log_file_location = utils.get_log_file_path(base_download_location)

    while current_date <= to_date:

        image_urls = extract_all_image_urls(current_date)
        download_location = os.path.join(base_download_location, str(current_date.year), str(current_date.month))
        if not os.path.isdir(download_location):
            os.makedirs(download_location)
        print(str(current_date) + ": " + str(len(image_urls)) + " images")
        Pool(10).map(lambda url: download_image(url, download_location), image_urls)
        # for image_url in image_urls:
        #    download_image(image_url, download_location)

        with open(log_file_location, 'wb') as handle:
            pickle.dump(current_date, handle)

        current_date += datetime.timedelta(1)


def download_image(image_url, download_location):
    filename = utils.extract_filename_from_url(image_url)
    full_filename = os.path.join(download_location, filename)

    if not os.path.isfile(full_filename):

        urllib.request.urlretrieve(image_url, full_filename)
        logging.debug(f"Saved {full_filename}")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Wrong number of arguments. Usage: python bing_image_downloader.py destination_folder")
        quit()
    logging.basicConfig(level=logging.DEBUG)
    path = sys.argv[1]

    if not os.path.isdir(path):
        print("Specified destination is not a valid folder.")
        quit()

    update_image_library(path)

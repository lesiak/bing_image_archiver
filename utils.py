import os


def extract_filename_from_url(url):
    """ Utility function used to extract a file name from an image url. """
    return url[url.rfind('/')+1:]


def get_log_file_path(download_folder):
    """ Utility function returning the path the the last_date_scanned.pickle log file from the download location of the
     images. """

    return os.path.join(download_folder, '_last_date_scanned.pickle')
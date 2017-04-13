import datetime
import re
import urllib.request
import logging

from html.parser import HTMLParser


class ImageUrlsExtractingParser(HTMLParser):
    """HTMLParser used to extract the url of Bing images from a Blog Post Attachment Page from www.iorise.com
    (e.g.: http://www.iorise.com/blog/?attachment_id=44)"""

    def __init__(self, result_list):
        """ Constructor: Initialize parser. """

        HTMLParser.__init__(self)

        self.result_list = result_list

        # Regex used to validate the href attribute of a tags
        self.href_chk = re.compile('^http://www[.]iorise[.]com/blog/wp-content/uploads/20[0-9]{2}/[01][0-9]/.+[.](jpg|jpeg)$')

    def handle_starttag(self, tag, attrs):
        """ Method called when the parser encounter a start tag. """

        # The url to the image will be in an achor tag
        if tag == 'a':

            # Check if we are currently at the right a tag
            if self.validate_a_tag(attrs):
                for attr_name, attr_value in attrs:
                    if attr_name == 'href':
                        self.result_list.append(attr_value)

    def validate_a_tag(self, attrs):
        """ Method called to check if a <a> tag and its attributes correspond to what we're looking for. """

        href_ok = False
        rel_ok = False

        for attribute_name, value in attrs:
            # Check the href
            if attribute_name == 'href':
                if self.href_chk.match(value):
                    href_ok = True

            # Check the rel
            elif attribute_name == 'rel':
                #if value == 'attachment':
                 #   rel_ok = True
                return False

            # The tag should not contain any more attributes
            else:
                return False

        return href_ok

    def error(self, message):
        print(message)


class AttachmentPageExtractingParser(HTMLParser):
    """HTMLParser used to extract the url of attachment page containing the Bing images from a Day Page from
    www.iorise.com (e.g.: http://www.iorise.com/blog/?m=20121125)"""

    def __init__(self, result_list):
        """ Constructor: Initialize parser. """

        HTMLParser.__init__(self)

        self.result_list = result_list

        # Regex used to validate the href attribute of a tags
        self.href_chk = re.compile('^http://www[.]iorise[.]com/(blog/)?[?]attachment_id=[0-9]+$')
        self.rel_chk = re.compile('^attachment wp-att-[0-9]+$')

    def handle_starttag(self, tag, attrs):
        """ Method called when the parser encounter a start tag. """

        # The url we are looking for will be in an <a> tag
        if tag == 'a':

            # Check if we are currently at the right a tag
            if self.validate_a_tag(attrs):
                for attr_name, attr_value in attrs:
                    if attr_name == 'href':
                        self.result_list.append(attr_value)

    def validate_a_tag(self, attrs):
        """ Method called to check if a <a> tag and its attributes correspond to what we're looking for. """

        href_ok = False
        rel_ok = False

        for attribute_name, value in attrs:
            # Check the href
            if attribute_name == 'href':
                if self.href_chk.match(value):
                    href_ok = True

            # Check the rel
            elif attribute_name == 'rel':
                if self.rel_chk.match(value):
                    rel_ok = True

            # The tag should not contain any more attributes
            else:
                return False

        return href_ok and rel_ok

    def error(self, message):
        print(message)


def extract_all_image_urls(date_to_extract):
    """ Function used to extract all Bing images of the day published on iorise between the two provided dates. """

    url = "http://www.iorise.com/blog/?m={year}{month:02}{day:02}".format(year=date_to_extract.year,
                                                                    month=date_to_extract.month,
                                                                    day=date_to_extract.day)

    new_format = has_urls_in_page(date_to_extract)
    if new_format:
        return extract_urls_from_page_with_urls(url)

    attachment_pages_urls = extract_attachment_pages_urls(url)

    all_image_urls = []
    # For each attachment page, extract the image urls
    for page_url in attachment_pages_urls:
        image_urls = extract_urls_from_page_with_urls(page_url)
        all_image_urls += image_urls

    return all_image_urls


def has_urls_in_page(date_to_extract):
    new_format_change_date = datetime.date(2014, 10, 8)
    return date_to_extract >= new_format_change_date


def extract_attachment_pages_urls(url):
    try:
        logging.debug(f"Fetching page {url}")
        page_resp = urllib.request.urlopen(url)
    except urllib.request.HTTPError as e:
        logging.warning(f"Could not fetch page {url} {e}")
        return []

        # Extract attachment pages from day page
    attachment_pages_urls = []
    day_page_parser = AttachmentPageExtractingParser(attachment_pages_urls)
    day_page_parser.feed(page_resp.read().decode('UTF-8'))
    return attachment_pages_urls


def extract_urls_from_page_with_urls(page_url):
    try:
        attachment_page_resp = urllib.request.urlopen(page_url)
    except urllib.request.HTTPError as e:
        logging.error(f"Could not fetch page {page_url} {e}")
        return []

    image_urls = []
    parser = ImageUrlsExtractingParser(image_urls)
    parser.feed(attachment_page_resp.read().decode('UTF-8'))
    return image_urls

import re
import urllib.request
import logging

from html.parser import HTMLParser


class BlogAttachmentPageParser(HTMLParser):
    """HTMLParser used to extract the url of Bing images from a Blog Post Attachment Page from www.iorise.com
    (e.g.: http://www.iorise.com/blog/?attachment_id=44)"""

    def error(self, message):
        print(message)

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


class BlogDayPageParser(HTMLParser):
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


def extract_all_image_urls(date_to_extract):
    """ Function used to extract all Bing images of the day published on iorise between the two provided dates. """

    url = "http://www.iorise.com/blog/?m={year}{month:02}{day:02}".format(year=date_to_extract.year,
                                                                    month=date_to_extract.month,
                                                                    day=date_to_extract.day)

    try:
        logging.debug(f"Fetching page {url}")
        page = urllib.request.urlopen(url)
    except Exception as e:
        logging.warning(f"Could not fetch page {url}")
        return []

    # Extract attachment pages from day page
    attachment_pages_url = []
    day_page_parser = BlogDayPageParser(attachment_pages_url)
    day_page_parser.feed(page.read().decode('UTF-8'))

    all_image_urls = []

    # For each attachment page, extract the image urls
    for page_url in attachment_pages_url:

        try:
            attachment_page = urllib.urlopen(page_url)
        except:
            continue

        image_urls = []
        parser = BlogAttachmentPageParser(image_urls)
        parser.feed(attachment_page.read().decode('UTF-8'))

        all_image_urls += image_urls

    return all_image_urls



import logging
import requests
import time
import os
import sys
import json

# Hide the InsecureRequestWarning from urllib3
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import html2text
# https://gist.github.com/chrisguitarguy/1305010


class ScrapeUrl:

    def __init__(self, url=None, ogdata=None, tdata=None):
        try:
            self.sd = {}

            self.ogdata = ['title', 'type', 'description', 'image', 'url', 'locale']
            self.tdata = ['card', 'site', 'site:id', 'creator', 'creator:id', 'description', 'title', 'image',
                          'image:alt']

            if ogdata is not None:
                self.ogdata = ogdata

            if tdata is not None:
                self.tdata = tdata

            self.urlContent = None

            if url is None:
                self.sd = None

            self.sd['url'] = url

            base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url))
            self.sd['base_url'] = base_url

            self.url = url

            if self.getUrlContent() is False:
                self.sd = None

            if self.parseContent() is False:
                self.sd = None

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))

    def getUrlContent(self):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

            r = requests.get(self.url, headers=headers, timeout=10, verify=False)
            # status code not 200, houston we have a problem
            if 200 != r.status_code:
                return False

            self.urlContent = r.content
            self.sd['urlSpeed'] = r.elapsed.total_seconds()
            self.sd['urltimestamp'] = str(int(time.time()))

            return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))

    def parseContent(self):
        try:
            if self.urlContent is None:
                return False

            errors = []

            soup = BeautifulSoup(self.urlContent, 'html.parser')

            data = soup.find('title')
            self.sd['title'] = data.contents[0]

            for tag in soup.find_all("meta"):
                #get Facebook OpenGraph tags
                ogTags = []
                for od in self.ogdata:
                    field = "og:{}".format(od)
                    if tag.get("property", None) == field:
                        ogTags.append({field: tag.get("content", None)})

                #get Twitter cards
                for t in self.tdata:
                    field = "twitter:{}".format(t)
                    TTags = []
                    if tag.get("property", None) == field:
                        TTags.append({field: tag.get("content", None)})

                if tag.get("name", None) == "description":
                    self.sd['metadescription'] = tag.get("content", None)
                if tag.get("name", None) == "keywords":
                    self.sd['metakeywords'] = tag.get("content", None)

                if tag.get("name", None) == "generator":
                    self.sd['generator'] = tag.get("content", None)

            self.sd['ogTags'] = ogTags
            self.sd['twitterTags'] = TTags

            self.sd['charset'] = soup.meta.get('charset')

            # START IMAGES
            imglist = []
            for image in soup.findAll("img"):
                imglist.append({'alt': image.get('alt', ''), 'src': image.get('src', ''), 'width': image.get('width', ''),
                            'height': image.get('height', '')})

            self.sd["images"] = imglist
            # END IMAGES

            #START H1
            data = soup.find_all('h1')
            h1list = []
            for d in data:
                h1list.append(d.contents[0])

            self.sd['h1'] = h1list
            # END H1

            # START H2
            data = soup.find_all('h2')
            h2list = []
            for d in data:
                h2list.append(d.contents[0])

            self.sd['h2'] = h2list
            # END H2

            #retreive application ld+json
            SearchAction = 0
            for ld in soup.find_all('script', type='application/ld+json'):
                ldjson = json.loads(ld.text)
                try:
                    if ldjson['potentialAction']['@type'] == "SearchAction":
                        SearchAction = 1
                except KeyError as e:
                    continue

            if SearchAction == 0:
                errors.append('No Google Search Action found')

            #remove all style and scripts (also for within body)
            i = 0
            for script in soup.body(["script"]):
                if i == 0:
                    errors.append('Script found within Body')
                    i += 1
                script.extract()  # rip it out

            i = 0
            for script in soup.body(["style"]):
                if i == 0:
                    errors.append('Style found within Body')
                    i += 1
                script.extract()  # rip it out

            data = soup.body.find('article')

            print(data)

            if data is None:
                data = soup.body.find("main", {"id": "content"})

            if data is None:
                data = soup.body.find("div", {"class": "entry-content"})

            if data is None:
                data = soup.body.find("div", {"class": "page-content"})

            if data is None:
                data = soup.body.find("div", {"id": "content"})

            if data is None:
                data = soup.body

            text = data.get_text()

            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = ' '.join(chunk for chunk in chunks if chunk)


            self.sd['site_text'] = text
            self.sd['word_count'] = self.word_count(text)
            self.sd['pageerrors'] = errors

            #   <link rel="pingback"
            #   <link rel="shortcut icon"

            #is there structured data

            return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))


    def word_count(self, string):
        tokens = string.split()
        count = len(tokens)
        return count

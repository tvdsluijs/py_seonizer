import logging
import requests
# import time
import sys
import os
# import re

# Hide the InsecureRequestWarning from urllib3
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from bs4 import BeautifulSoup
# https://gist.github.com/chrisguitarguy/1305010


not_parseable_ressources = (
    ".epub", ".mobi", ".docx", ".doc", ".opf", ".7z", ".ibooks", ".cbr", ".avi", ".mkv", ".mp4", ".jpg",
    ".jpeg", ".png", ".gif", ".pdf", ".iso", ".rar", ".tar", ".tgz", ".zip", ".dmg", ".exe")


class SiteMap:

    def __init__(self, site=None):
        try:
            self.xml_list = []
            self.url_list = []

            if site is None:
                return None

            self.site = site

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))

    def readSitemaps(self):
        try:
            robots = self.site + "/robots.txt"
            robots = robots.replace('//robots.txt', '/robots.txt')

            sitemap_xml = False

            #try to get the robots file
            response = self.readSitemapUrl(robots, 0)
            if response:
                #try to parse sitemap variable from robotes
                data = self.robots(response)
                try:
                    sitemap = data['Sitemap']
                    sitemap_xml = self.readSitemapUrl(sitemap, 1)

                except KeyError as e:
                    sitemap_xml = False

            #no sitemap found yet? Then try the obvious sitemaps
            if sitemap_xml == False:
                sitemaps = ['sitemap.xml', 'sitemap_index.xml']
                for s in sitemaps:
                    sm = self.site + "/{}".format(s)
                    sm = sm.replace('//{}', '/{}').format(s, s)

                    sitemap_xml = self.readSitemapUrl(sm, 1)

                    if sitemap_xml is not False:
                        break;

            # no sitemaps found!
            if sitemap_xml == False:
                return False

            #get the sitemaps from the sitemap xml
            self.getSitemapUrls(sitemap_xml)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))


    def robots(self,file):
        try:
            self.robottxt = dict(line.strip().split(': ') for line in file.splitlines())

            return self.robottxt

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))


    def readSitemapUrl(self, url, response=0):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

            r = requests.get(url, headers=headers, timeout=10, verify=False)
            # status code not 200, houston we have a problem
            if 200 != r.status_code:
                return False

            if response == 0:
                return r.text
            else:
                return r.content

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))


    def getSitemapUrls(self, sitemap):
        try:

            # BeautifulStoneSoup to parse the document
            soup = BeautifulSoup(sitemap, 'lxml-xml')

            # find all the <url> tags in the document
            urls = soup.findAll('sitemap')

            # no urls? try if there are urls
            if not urls:
                urls = soup.findAll('url')

            if not urls:
                return False

            # extract what we need from the url
            for u in urls:
                url = u.find('loc').string
                if url.endswith('.xml'):
                    self.xml_list.append(url)
                    sitemap_xml = self.readSitemapUrl(url, 1)
                    self.getSitemapUrls(sitemap_xml)
                else:
                    self.url_list.append(url)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))

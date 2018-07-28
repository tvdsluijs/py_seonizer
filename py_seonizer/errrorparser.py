import logging
import os
import sys
import requests
import urllib.parse
import validators

class ErrorParser:

    def __init__(self, data=None, ogdata=None, tdata=None):
        try:
            self.ogdata = ['title', 'type', 'description', 'image', 'url', 'locale']
            self.tdata = ['card', 'site', 'site:id', 'creator', 'creator:id', 'description', 'title', 'image',
                          'image:alt']

            if ogdata is not None:
                self.ogdata = ogdata

            if tdata is not None:
                self.tdata = tdata

            if data is not None:

                self.errors = {}

                self.data = data
                self.url = self.data['url']

                self.title_errors()
                self.image_errors()
                self.h1_errors()
                self.body_text()
                self.og_errors()
                self.meta_errors()
                self.error_errors()
            else:
                self.errors = None

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))

    def title_errors(self):
        try:
            if self.data['title']:

                if len(self.data['title']) <= 0:
                    self.errors['title'] = {'url': self.url, 'severity': 1, 'title': self.data['title'], 'error': "No Title"}
                    return True

                if len(self.data['title']) <= 20:
                    self.errors['title'] = {'url': self.url, 'severity': 2,'title': self.data['title'], 'error': "Title to short"}
                    return True

                if len(self.data['title']) >= 60:
                    self.errors['title'] = {'url': self.url, 'severity': 2, 'title': self.data['title'], 'error': "Title to Long"}
                    return True

            #40 is about right

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))


    def image_errors(self):
        try:
            imgerrors = []
            if self.data['images']:
                images = self.data['images']
                for img in images:

                    src = images[img].get("src")

                    if src is None or src == '':
                        imgerrors.append({'url': self.url, 'severity': 1, 'img': src,
                                          'error': "No imgage src"})

                    base_url = self.data['base_url']
                    if src is not None and src != '':
                        if not validators.url(src):
                            imgscr = urllib.parse.urljoin(base_url, src)
                            print(src)

                        # check for https:// or http or //
                        #     NO ?
                        #     ADD URL
                        #
                        # check again for // in URL (not https://)




                        r = requests.head(imgscr)

                        if 200 != r.status_code:
                            errorstr = "status code : {}".format(r.status_code)
                            imgerrors.append({'url': self.url, 'severity': 1, 'img': src,
                                              'error': errorstr})

                    alt = images[img].get("alt")
                    if alt is None or alt == '':
                        imgerrors.append({'url': self.url, 'severity': 3, 'img': src,
                                          'error': "No Alt-text"})

                    height = images[img].get("height")
                    if height is None or int(height) <= 0:
                        imgerrors.append({'url': self.url, 'severity': 3, 'img': src,
                                          'error': "No height"})

                    width = images[img].get("width")
                    if width is None or int(width) <= 0:
                        imgerrors.append({'url': self.url, 'severity': 3, 'img': self.data['src'],
                                          'error': "No width"})

            self.errors['images'] = imgerrors

        except KeyError as e:
            self.errors['images'] = [{'url': self.url, 'severity': 1, 'img': "0", 'error': "Error reading images"}]
            return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))


    def h1_errors(self):
        try:
            i = 0
            if len(self.data['h1']) <= 0:
                raise KeyError('none')

            for h in self.data['h1']:
                if len(h) <= 5:
                    self.errors['h1'][i] = {'url': self.url, 'severity': 4, 'h1': self.data['h1'], 'error': "Short H1-text"}
                if len(h) > 50:
                    self.errors['h1'][i] = {'url': self.url, 'severity': 4, 'h1': self.data['h1'],
                                            'error': "Long H1-text"}
                i += 1

            if i > 1:
                self.errors['h1'][i] = {'url': self.url, 'severity': 1, 'h1': ">1", 'error': "Multiple H1-text"}

        except KeyError as e:
            self.errors['h1'][i] = {'url': self.url, 'severity': 1, 'h1': "0", 'error': "No H1-text"}
            return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))


    def body_text(self):
        try:
            if self.data['site_text']:

                if self.data['word_count'] <= 0:
                    raise KeyError('none')

                if self.data['word_count'] <= 300:
                    self.errors['site_text'] = {'url': self.url, 'severity': 1, 'content': "<300", 'error': "To little content"}
                    return True

                if self.data['word_count'] > 2000:
                    self.errors['site_text'] = {'url': self.url, 'severity': 4, 'content': ">2000", 'error': "Much content"}
                    return True

        except KeyError as e:
            self.errors['site_text'] = {'url': self.url, 'severity': 1, 'content': "0", 'error': "No content"}
            return True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))


    def og_errors(self):
        try:
            i = 0
            for f in self.ogdata:
                try:
                    field = "og:{}".format(f)
                    if len(self.data[field]) <= 0:
                        raise KeyError('None')
                except KeyError as e:
                    error = "No og {}".format(f)
                    self.errors['og'][i] = {'url': self.url, 'severity':5,'title': self.data['title'], 'error': error}
                    i += 1

            for f in self.tdata:
                try:
                    field = "twitter:{}".format(f)
                    if len(self.data[field]) <= 0:
                        raise KeyError('None')
                except KeyError as e:
                    error = "No twitter {}".format(f)
                    self.errors['twitter'][i] = {'url': self.url, 'severity': 5, 'title': self.data['title'], 'error': error}
                    i += 1

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))


    def meta_errors(self):
        try:
            try:
                if len(self.data['metadescription']) <= 0:
                    raise KeyError('None')
            except KeyError as e:
                self.errors['metadescription'] = {'url': self.url, 'severity': 2, 'content': "0", 'error': "No Meta Description"}

            try:
                if len(self.data['metakeywords']) <= 0:
                    raise KeyError('None')
            except KeyError as e:
                self.errors['metakeywords'] = {'url': self.url, 'severity': 2, 'content': "0", 'error': "No Meta keywords"}

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))

    def error_errors(self):
        try:
            i = 0
            for e in self.data['pageerrors']:
                self.errors['global'][i] = e
                i += 1
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))

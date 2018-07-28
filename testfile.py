from py_seonizer import Sitemap
from py_seonizer import ScrapeUrl
from py_seonizer import ErrorParser

ogdata = ['title', 'type', 'description', 'image', 'url', 'locale']
tdata = ['card', 'site', 'site:id', 'creator', 'creator:id', 'description', 'title', 'image',
              'image:alt']

url = "https://oesterbaron.nl/"
url = "https://oesterbaron.nl/aanbevolen/winterproof/"
url = "https://zldsteigerbouw.nl/"
url = "https://zldsteigerbouw.nl/welke-diensten-bieden-aan/"
url = "https://www.dejastone.nl/composiet/"
url = "https://www.urnenhemel.nl/winkel/assieraden-assieraad/assieraad-dierenurn-hondenpootje-zwart/"

url = "https://vandersluijs.nl/blog/2014/10/installatie-mongodb.html"
s = ScrapeUrl(url, ogdata, tdata)

print(s.sd['base_url'])

# if s.sd is not None:
#     e = ErrorParser(s.sd, ogdata, tdata)
#     if e.errors is not None and len(e.errors) > 0:
#         print(e.errors)
#     else:
#         print('Could not find errors')
#
# else:
#     print('Could not find shit!')

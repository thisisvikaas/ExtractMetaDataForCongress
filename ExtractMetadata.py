""" Meta tags that Google understands - https://support.google.com/webmasters/answer/79812?hl=en
    Google search understands the name tag with 'DESCRIPTION' attribute for a a short description of the page"""

from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
from my_fake_useragent import UserAgent
import itertools
import re
import time

# Mimic the access to the website like a browser
ua = UserAgent(family='chrome')
BrowserUserAgent = ua.random()

pages = []
MetaList = []
WebsitesMissingKey = []
ConPlusWeblist = []
FoundList = []
counter = 0
headers = BrowserUserAgent


def Write2CSV(filename, givenList):
    with open(filename, 'w', encoding="utf-8", newline="\n") as myFile:
        wr = csv.writer(myFile, lineterminator="\n")
        for val in givenList:
            wr.writerow([val])


def RemoveTags(givenList):
    givenList = [re.sub(r'<[^>]+>', '', item) for item in givenList]
    return givenList


conferenceFrame = pd.read_csv('ConferencesWithWebsites.csv', names=['Conference', 'Website'],
                              encoding='unicode_escape')
WebsiteList = conferenceFrame['Website'].tolist()
ConferenceList = conferenceFrame['Conference'].tolist()

ConPlusWeblist = [(conference + "#" + url) for (url, conference) in itertools.zip_longest(WebsiteList, ConferenceList)]

print("Fetched {}".format(len(WebsiteList)) + " Conference Websites")

for (url, conference) in itertools.zip_longest(WebsiteList, ConferenceList):
    try:
        page = requests.get(url, headers, verify=False)
        soup = BeautifulSoup(page.text, 'html.parser')
        metas = soup.find_all('meta')
        time.sleep(2)
        for meta in metas:
            if 'name' in meta.attrs and meta['name'] in ('description', 'DESCRIPTION', 'Description','og:description') and len(
                    meta.attrs['content']) > 0:
                MetaList.append((conference + "#" + url + "$" + meta.attrs['content']))
                FoundList.append(conference + "#" + url)
    except KeyError:
        WebsitesMissingKey.append(conference + "#" + url)
        continue

# Remove HTML Tags
MetaList = RemoveTags(MetaList)
FoundList = RemoveTags(FoundList)
WebsitesMissingKey = RemoveTags(WebsitesMissingKey)

# Writing Results to CSV
Write2CSV('WebsitesWithMetaData.csv', MetaList)

# Missing Meta Data Websites
MissingList = list(set(ConPlusWeblist) - set(FoundList))
Write2CSV('WebsitesWithMissingMeta.csv', MissingList)
Write2CSV('WebsitesWithMissingKey.csv', WebsitesMissingKey)

print("Meta Data Extracted For " + "{:.1%}".format(len(MetaList) / len(WebsiteList)), "Of Websites")
print("Meta Data Not Found For {}".format(len(MissingList)), "Websites")

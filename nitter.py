import requests
from bs4 import BeautifulSoup
 
class ReadRss:
    def __init__(self, rss_url, headers):
        self.url = rss_url
        self.headers = headers
        try:
            self.r = requests.get(rss_url, headers=self.headers)
            self.status_code = self.r.status_code
        except Exception as e:
            print('Error fetching the URL: ', rss_url)
            print(e)
        try:    
            self.soup = BeautifulSoup(self.r.text, 'xml')
        except Exception as e:
            print('Could not parse the xml: ', self.url)
            print(e)
        self.tweets = self.soup.findAll('item')
        self.tweets_dicts = [{'title':a.find('title').text, 'creator':a.find('dc:creator').text,'description':a.find('description').text,'pub_date':a.find('pubDate').text} for a in self.tweets]
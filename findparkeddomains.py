import requests
import re
from urllib.parse import urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ParkedSearch(object):
    def __init__(self, timeout: int=5, allow_insecure: bool=True, accept_new_domain: bool=True):
        self.timeout = timeout
        self.allow_insecure = allow_insecure
        self.accept_new_domain = accept_new_domain
        self.cache = {}

    def is_content_parked(self, content):
        return any(re.findall(r'buy this domain|parked free|godaddy|is for sale'
                            r'|domain parking|renew now|this domain|namecheap|buy now for'
                            r'|hugedomains|is owned and listed by|sav.com|searchvity.com'
                            r'|domain for sale|register4less|aplus.net|related searches'
                            r'|related links|search ads|domain expert|united domains'
                            r'|domian name has been registered|this domain may be for sale'
                            r'|domain name is available for sale|premium domain'
                            r'|this domain name|this domain has expired|domainpage.io'
                            r'|sedoparking.com|parking-lander', content, re.IGNORECASE))

    def follow_url(self, url):
        try:
            res = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
                'Accept-Encoding': 'gzip',
                'Accept-Language': 'en-US',
                'Accept': 'text/html,application/xml,application/xhtml+xml',
            }, allow_redirects=False, timeout=self.timeout, verify=(not self.allow_insecure))
        except:
            return None
        if res.is_redirect:
            location = res.headers['location']
            target_domain = urlparse(self.url).netloc
            redirect_domain = urlparse(location).netloc
            if target_domain == redirect_domain or 'www.' + target_domain == redirect_domain or self.accept_new_domain:
                return self.follow_url(location)
        else:
            return res.text

    def is_parked_urls(self, urls):
        assert isinstance(urls, list), 'This method is reserved for lists, use .is_parked_url instead.'
        for url in urls:
            url = url if url.startswith('http') else 'http://' + url

            self.text_response = self.follow_url(url, self.timeout, self.allow_insecure, self.accept_new_domain)
            if self.text_response is None:
                self.cache.setdefault(url, 'Unresponsive')
            elif not self.is_content_parked(self.text_response):
                self.cache.setdefault(url, 'Active')
            elif self.is_content_parked(self.text_response):
                self.cache.setdefault(url, 'Parked')
        return self.cache

    def clear_cache(self):
        self.cache = {}
        if not self.cache:
            return True
        else:
            return False

    def is_parked_url(self, url):
        assert isinstance(url, str), 'This method is reserved for a single string, use .is_parked_urls instead for lists.'
        url = url if url.startswith('http') else 'http://' + url
        text_response = self.follow_url(self.url, self.timeout, self.allow_insecure, self.accept_new_domain)
        if text_response is None:
            self.cache.setdefault(url, 'Unresponsive')
        elif not self.is_content_parked(text_response):
            self.cache.setdefault(url, 'Active')
        elif self.is_content_parked(text_response):
            self.cache.setdefault(url, 'Parked')
        return self.cache

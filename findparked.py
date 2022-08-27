import requests
import re
from nslookup import Nslookup
from urllib.parse import urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ParkedSearch(object):
    def __init__(self, timeout: int=5, allow_insecure: bool=True, accept_new_domain: bool=True, dns_servers: list=[]):
        self.timeout = timeout
        self.allow_insecure = allow_insecure
        self.accept_new_domain = accept_new_domain
        self.dns_servers = dns_servers
        self.dns_resolution = None
        self.ip_count = None
        self.cache = {}
        self.ip_cache = {}

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
            target_domain = urlparse(url).netloc
            redirect_domain = urlparse(location).netloc
            if target_domain == redirect_domain or 'www.' + target_domain == redirect_domain or self.accept_new_domain:
                return self.follow_url(location)
        else:
            return res.text

    def is_parked_urls(self, urls):
        assert isinstance(urls, list), 'This method is reserved for lists, use .is_parked_url instead for a string url.'
        for url in urls:
            url = url if url.startswith('http') else 'http://' + url
            self.text_response = self.follow_url(url)
            if self.text_response is None:
                self.cache.setdefault(url, 'Unresponsive')
            elif not self.is_content_parked(self.text_response):
                self.cache.setdefault(url, 'Active')
            elif self.is_content_parked(self.text_response):
                self.cache.setdefault(url, 'Parked')
        return self.cache

    def is_parked_url(self, url):
        assert isinstance(url, str), 'This method is reserved for a single string, use .is_parked_urls instead for lists.'
        url = url if url.startswith('http') else 'http://' + url
        text_response = self.follow_url(url)
        if text_response is None:
            self.cache.setdefault(url, 'Unresponsive')
        elif not self.is_content_parked(text_response):
            self.cache.setdefault(url, 'Active')
        elif self.is_content_parked(text_response):
            self.cache.setdefault(url, 'Parked')
        return self.cache

    def verify_on_ips(self, urls, dns_servers: list=['1.1.1.1']):
        assert isinstance(urls, list), 'A list is required to use this method, otherwise the result will always be 0 or 1 for a count.'
        dns_query = Nslookup(dns_servers=dns_servers if not self.dns_servers else self.dns_servers if self.dns_servers else [], verbose=False, tcp=False)
        small_ip_cache = {}
        count_ip_cache = {}
        for url in urls:
            url = url if not url.startswith('http') else url.split('//')[1].strip('www.').rstrip('/')
            ips_record = dns_query.dns_lookup(url)
            small_ip_cache.setdefault(url, ips_record.answer)
        for ipx in small_ip_cache.values():
            for ix in ipx:
                for ip in small_ip_cache.values():
                    for p in ip:
                        if p == ix:
                            count_ip_cache.setdefault(p, 1) + 1
        self.ip_cache = {
            'dns_resolution': {**small_ip_cache},
            'ip_count': {**count_ip_cache}
        }
        self.dns_resolution = self.ip_cache['dns_resolution']
        self.ip_count = self.ip_cache['ip_count']

    def get_ip_cache(self):
        return self.ip_cache

    def get_cache(self):
        return self.cache
    
    def clear_cache(self):
        self.cache = {}
        if not self.cache:
            return True
        else:
            return False

    def clear_ip_cache(self):
        self.ip_cache = {}
        if not self.ip_cache:
            return True
        else:
            return False


#!/usr/bin/env python3

import requests
import re
from urllib.parse import urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def is_content_parked(content):
    return any(re.findall(r'buy this domain|parked free|godaddy|is for sale'
                          r'|domain parking|renew now|this domain|namecheap|buy now for'
                          r'|hugedomains|is owned and listed by|sav.com|searchvity.com'
                          r'|domain for sale|register4less|aplus.net|related searches'
                          r'|related links|search ads|domain expert|united domains'
                          r'|domian name has been registered|this domain may be for sale'
                          r'|domain name is available for sale|premium domain'
                          r'|this domain name|this domain has expired|domainpage.io'
                          r'|sedoparking.com|parking-lander', content, re.IGNORECASE))

def follow_url(url, timeout, allow_insecure, accept_new_domain):
    try:
        res = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'en-US',
            'Accept': 'text/html,application/xml,application/xhtml+xml',
        }, allow_redirects=False, timeout=timeout, verify=(not allow_insecure))
    except:
        return None

    if res.is_redirect:
        location = res.headers['location']
        target_domain = urlparse(url).netloc
        redirect_domain = urlparse(location).netloc
        if target_domain == redirect_domain or 'www.' + target_domain == redirect_domain or accept_new_domain:
            return follow_url(location, timeout, allow_insecure, accept_new_domain)
    else:
        return res.text

def is_parked_urls(urls, accept_new_domain, allow_insecure, timeout):
    cache = {}
    for url in urls:
        url = url if url.startswith('http') else 'http://' + url

        text_response = follow_url(url, timeout, allow_insecure, accept_new_domain)
        if text_response is None:
            cache.setdefault(url, 'Unresponsive')
        elif not is_content_parked(text_response):
            cache.setdefault(url, 'Active')
        elif is_content_parked(text_response):
            cache.setdefault(url, 'Parked')
    return cache
        

if __name__ == '__main__':
    # Sample sites -- but the domains themselves can be pulled in from any other resource
    sites = [
        'https://aclcare.com/',
        'https://googleparkedurl.com'
    ]

    is_parked_urls(sites, accept_new_domain=True, allow_insecure=True, timeout=5)

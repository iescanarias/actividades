from urllib.parse import urlparse, urlunparse, quote

def normalize(url):
    url = url.replace("\\", "/")
    parts = urlparse(url)
    return urlunparse(parts._replace(path=quote(parts.path)))

def encode(url):
    return quote(url)

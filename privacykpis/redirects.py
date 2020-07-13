import pathlib
import pickle
from typing import Dict, Optional
from urllib.parse import urlparse

from publicsuffixlist import PublicSuffixList  # type: ignore
import requests
import requests.exceptions


PSL = PublicSuffixList()
CHROME_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) "
             "AppleWebKit/537.36 (KHTML, like Gecko) "
             "Chrome/84.0.4147.85 "
             "Safari/537.36")
CHROME_HEADERS = {'user-agent': CHROME_UA}


class RedirectCache:
    path: Optional[pathlib.Path]
    cache: Dict[str, bool]

    def __init__(self, path: Optional[pathlib.Path]) -> None:
        self.cache = {}

        if path is None:
            return

        self.path = path
        if self.path.is_file():
            with self.path.open('rb') as handle:
                self.cache = pickle.load(handle)

    def is_redirect(self, url: str) -> bool:
        netloc = urlparse(url).netloc

        try:
            return self.cache[netloc]
        except KeyError:
            pass

        all_same_etldp1 = self.is_all_same_etldp1_in_request_chain(url)
        was_redirected = not all_same_etldp1
        self.cache[netloc] = was_redirected
        return was_redirected

    def is_all_same_etldp1_in_request_chain(self, url: str) -> bool:
        try:
            etldp1 = PSL.privatesuffix(urlparse(url).netloc)
            rs = requests.get(url, headers=CHROME_HEADERS, timeout=5)
            for r in rs.history:
                request_etldp1 = PSL.privatesuffix(urlparse(r.url).netloc)
                if request_etldp1 != etldp1:
                    return False
            return True
        except requests.exceptions.RequestException:
            # Be pessimistic here; if were can't be sure its not
            # a redirection chain, assume it is.
            return False

    def write(self) -> bool:
        if self.path:
            with self.path.open('wb') as handle:
                pickle.dump(self.cache, handle)
            return True
        return False

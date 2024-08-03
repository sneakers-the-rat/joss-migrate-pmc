from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import re

from bs4 import BeautifulSoup

UID_PATTERN = re.compile(r'(?<=joss\.)\d{5}')


@dataclass
class JossPaper:
    path: Path
    _jats: Optional[BeautifulSoup] = None
    _crossref: Optional[BeautifulSoup] = None

    @property
    def jats_path(self) -> Optional[Path]:
        try:
            path = next(self.path.glob('*.jats'))
        except StopIteration:
            return None
        if path.is_dir():
            try:
                return next(path.glob('*.jats'))
            except StopIteration:
                return None
        else:
            return path

    @property
    def crossref_path(self):
        return next(self.path.glob('*.crossref.xml'))

    @property
    def crossref(self) -> BeautifulSoup:
        if self._crossref is None:
            with open(self.crossref_path, 'r') as f:
                self._crossref = BeautifulSoup(f, 'xml')
        return self._crossref

    @property
    def jats(self) -> Optional[BeautifulSoup]:
        if not self._jats:
            if self.jats_path is None:
                return None
            with open(self.jats_path, 'r') as jfile:
                self._jats = BeautifulSoup(jfile, 'xml')
        return self._jats

    @property
    def doi(self) -> str:
        if self.jats is not None:
            return self.jats.find(attrs={'pub-id-type':'doi'}).text
        return self.crossref.find(attrs={'id_type':'doi'}).text

    @property
    def uid(self) -> str:
        return UID_PATTERN.search(self.doi).group()

    @property
    def volume(self) -> int:
        if self.jats is not None:
            return int(self.jats.find('volume').text)
        return int(self.crossref.find('volume').text)

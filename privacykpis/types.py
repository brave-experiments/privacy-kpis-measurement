from abc import abstractmethod, abstractproperty
import csv
from typing import Any, Dict, List, Union

from privacykpis.tokenizing import TokenLocation


class CSVWriter:
    @abstractmethod
    def writerow(self, row: List[str]) -> None:
        pass

    @abstractmethod
    def writerows(self, rows: List[List[str]]) -> None:
        pass

    @abstractproperty
    def dialect(self) -> csv.Dialect:
        pass


RequestRec = Dict[Union[TokenLocation, str], Any]

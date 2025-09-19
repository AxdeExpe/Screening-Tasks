import os
import re
import pandas as pd
from datetime import datetime
from typing import Iterator, Tuple

class OHLCDataReader:
    def __init__(self, path: str = "btc-1h.csv"):

        self.path = path

        if not os.path.exists(self.path):
            raise FileNotFoundError

        if not re.search(r"\.csv$", self.path):
            raise ValueError("File is not a .csv")
        
        if not os.access(self.path, os.R_OK):
            raise PermissionError("File is not readable")
        
        if os.stat(self.path).st_size == 0:
            raise ValueError("File is empty")
        
        self.pd_file = pd.read_csv(self.path).dropna()
        self.header = self.pd_file.columns.values

    def get_header(self) -> list:
        return list(self.header)
    
    def _is_unix_time(self, timestamp: int) -> bool:

        return 1e11 <= timestamp <= 2e13

    def get_time_diff(self, time1: int, time2: int) -> int:

        if not self._is_unix_time(time1) or not self._is_unix_time(time2):
            raise ValueError("Not UnixTime")
        
        return abs(time2 - time1)



    def read(self) -> Iterator[Tuple]:
        for index, row in self.pd_file.iterrows():
            yield tuple(row[col] for col in self.header)





class OHLCAnalyzer:
    def __init__(self, ohlc_reader: OHLCDataReader):
        self.ohlc_reader = ohlc_reader
        self.close_time_name = None
        self.close_price_name = None

    def set_close_time_name(self, close_time_name: str) -> None:

        header = self.ohlc_reader.get_header()

        if close_time_name not in header:
            raise ValueError("Close time name not in header")
        
        self.close_time_name = close_time_name

    def set_close_price_name(self, close_price_name: str) -> None:

        header = self.ohlc_reader.get_header()

        if close_price_name not in header:
            raise ValueError("Close price name not in header")

        self.close_price_name = close_price_name

    def _replace_first_none(self, ohlc_pair: list, value: tuple) -> None:
        for i, v in enumerate(ohlc_pair):
            if v is None:
                ohlc_pair[i] = value
                break

    def analyze_close_change(self, percent_diff: float = 3.0, time_interval: int = 60 * 60 * 1000) -> Iterator[Tuple[float, list]]: # 1 hour

        if self.close_price_name is None or self.close_time_name is None:
            raise ValueError("Close price name or close time name is not set")

        if percent_diff < 0.0 or percent_diff > 100.0:
            raise ValueError("percent diff must be between 0 and 100")

        header = self.ohlc_reader.get_header()
        close_time_index = header.index(self.close_time_name)
        close_price_index = header.index(self.close_price_name)

        ohlc_pair = [None, None]

        for row in self.ohlc_reader.read():

            self._replace_first_none(ohlc_pair, row)

            if ohlc_pair[-1] is not None:
                time_diff = self.ohlc_reader.get_time_diff(int(ohlc_pair[0][close_time_index]), int(ohlc_pair[1][close_time_index]))

                if time_diff != time_interval:
                    raise ValueError("Time diff is not equal to time_interval")

                price_change_percent = (ohlc_pair[0][close_price_index] - ohlc_pair[1][close_price_index]) / ohlc_pair[0][close_price_index] * 100
                price_change_percent_abs = abs(price_change_percent)

                if price_change_percent_abs > percent_diff:
                    yield price_change_percent_abs, ohlc_pair

                ohlc_pair[0] = ohlc_pair[1]
                ohlc_pair[1] = None

    def _convert_unix_to_datetime(self, unix_time: int) -> str:
        return datetime.fromtimestamp(unix_time / 1000).strftime('%Y-%m-%d %H:%M:%S')

    def show_first_n(self, n: int = 5, percent_diff: float = 3.0, time_interval: int = 60 * 60 * 1000) -> None:

        header = self.ohlc_reader.get_header()
        close_time_index = header.index(self.close_time_name)
        close_price_index = header.index(self.close_price_name)

        for i, (price_change_percent, ohlc_pair) in enumerate(self.analyze_close_change(percent_diff=percent_diff, time_interval=time_interval)):
            
            if i >= n:
                break

            close_time_start = self._convert_unix_to_datetime(int(ohlc_pair[0][close_time_index]))
            close_time_end = self._convert_unix_to_datetime(int(ohlc_pair[1][close_time_index]))
            print("{:<10.2f}% {:<10} {:<10} {:<10} {:<10}".format(price_change_percent, close_time_start, ohlc_pair[0][close_price_index], close_time_end, ohlc_pair[1][close_price_index]))



if __name__ == "__main__":
    
    ohlc_data_reader = OHLCDataReader()

    ohlc_analyzer = OHLCAnalyzer(ohlc_data_reader)
    ohlc_analyzer.set_close_time_name("close_time")
    ohlc_analyzer.set_close_price_name("close")

    ohlc_analyzer.show_first_n(n=20, percent_diff=5)
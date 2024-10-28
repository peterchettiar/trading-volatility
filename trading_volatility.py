import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TradingVolatility:
    """This module defines the various strategies prescribed by the research article"""

    def __init__(self, tickers_list: list):
        self.tickers_list = tickers_list

    def get_data(
        self, start_date: str, end_date: str, col_rename:str, manual_loading=None) -> pd.DataFrame:
        """Function to merge historical data from yahoo finance with manual uploads"""
        if manual_loading is not None and manual_loading.endswith(".csv"):
            manual_upload = pd.read_csv(manual_loading, usecols=['Date','Open'], parse_dates=['Date']).sort_values(by='Date', ascending=True).set_index('Date')
            manual_upload.rename(columns={"Open": col_rename}, inplace=True)
            logger.info("File loaded successfully.")
        else:
            raise ValueError("File path is either None or not a CSV file.")

        for ticker in self.tickers_list:

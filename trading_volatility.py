import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TradingVolatility:
    """This module defines the various strategies prescribed by the research article"""

    def __init__(self, tickers_list: list | dict):
        self.tickers_list = tickers_list

    def _manual_upload(self, filepath:str, col_rename: str):
         manual_upload = pd.read_csv(filepath, usecols=['Date','Open'], parse_dates=['Date'])\
            .sort_values(by='Date', ascending=True).set_index('Date')
         manual_upload.rename(columns={"Open": col_rename}, inplace=True)

         return manual_upload
    
    def _get_data_tickers_dict(self, start_date, end_date):
        tickers_dict = self.tickers_list

        stock_data = pd.DataFrame()

        for key, value in tickers_dict.items():
            hist_price = yf.download(key, start=start_date, end=end_date)[value]

            if not hist_price.empty:
                if stock_data.empty:
                    stock_data = hist_price
                else:
                    stock_data = pd.merge(stock_data, hist_price, left_index=True, right_index=True)

        stock_data.index = stock_data.index.tz_convert(None)
        stock_data.columns = [f'{ticker.lower()}_{pos.lower()}' for pos, ticker in stock_data.columns]

        return stock_data
    
    def _get_data_tickers_list(self, start_date, end_date):
        tickers_list = self.tickers_list

        stock_data_df = pd.DataFrame()

        for ticker in tickers_list:
            hist_price_df = yf.download(ticker, start=start_date, end=end_date)[["Open","Close"]]
            if not hist_price_df.empty:
                if stock_data_df.empty:
                    stock_data_df = hist_price_df
                else:
                    stock_data_df = pd.merge(stock_data_df, hist_price_df, left_index=True, right_index=True)
            
        stock_data_df.index = stock_data_df.index.tz_convert(None)
        stock_data_df.columns = [f'{ticker.lower()}_{pos.lower()}' for pos, ticker in stock_data_df.columns]

        return stock_data_df

    def get_data(self, start_date: str, end_date: str, col_rename: str, manual_loading=None) -> pd.DataFrame:
        """Function to merge historical data from yahoo finance with manual uploads"""
        if manual_loading is not None and manual_loading.endswith(".csv"):
            manual_upload = self._manual_upload(manual_loading, col_rename)
            logger.info("File loaded successfully.")
        else:
            raise ValueError("File path is either None or not a CSV file.")
        
        if isinstance(self.tickers_list, dict):
            yf_data = self._get_data_tickers_dict(start_date=start_date, end_date=end_date)
        else:
            yf_data = self._get_data_tickers_list(start_date=start_date, end_date=end_date)

        return yf_data.join(manual_upload[col_rename])
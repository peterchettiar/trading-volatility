"""
This project builds a modular library of volatility trading strategies based on 
concepts from the research paper "Trading Strategies Based on the VIX Term Structure." 

Focused on VIX term structure strategies, this project aims to reproduce and expand
on the paper’s findings, making it easier to analyze, test, and integrate these 
strategies into an algorithmic trading setup. The modular design allows for
individual strategy adaptation and offers a foundation for further development in 
volatility-based algorithmic trading.

For more information, refer to the original research paper:
https://github.com/peterchettiar/trading-volatility/blob/main/FULLTEXT01.pdf.
"""

import logging
import math
import yfinance as yf
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TradingVolatility:
    """This class defines a modular framework for replicating VIX-based trading strategies"""

    def __init__(
        self,
        volatility_indices: list,
        volatility_assets: list,
    ):
        """Initializes the TradingVolatility instance with specified tickers"""

        self.volatility_assets = volatility_assets
        self.volatility_indices = volatility_indices
        self.data = None

    def __manual_upload(self, filepath: str, col_rename: str):
        """Loads a CSV file with a date and price column for a manual data input"""

        manual_upload = (
            pd.read_csv(filepath, usecols=["Date", "Open"], parse_dates=["Date"])
            .sort_values(by="Date", ascending=True)
            .set_index("Date")
        )
        manual_upload.rename(columns={"Open": col_rename}, inplace=True)

        return manual_upload

    def __get_data_tickers_list(self, start_date, end_date):
        """Fetches historical open and close prices for tickers in list"""

        tickers_list = self.volatility_assets + self.volatility_indices

        stock_data_df = pd.DataFrame()

        for ticker in tickers_list:
            if ticker in self.volatility_assets:
                hist_price_df = yf.download(ticker, start=start_date, end=end_date)[
                    ["Open", "Close"]
                ]
                if not hist_price_df.empty:
                    if stock_data_df.empty:
                        stock_data_df = hist_price_df
                    else:
                        stock_data_df = pd.merge(
                            stock_data_df,
                            hist_price_df,
                            left_index=True,
                            right_index=True,
                        )
            else:
                hist_price_df = yf.download(ticker, start=start_date, end=end_date)[
                    ["Open"]
                ]
                if not hist_price_df.empty:
                    if stock_data_df.empty:
                        stock_data_df = hist_price_df
                    else:
                        stock_data_df = pd.merge(
                            stock_data_df,
                            hist_price_df,
                            left_index=True,
                            right_index=True,
                        )

        stock_data_df.index = stock_data_df.index.tz_convert(None)
        stock_data_df.columns = [
            f"{ticker.lower()}_{pos.lower()}" for pos, ticker in stock_data_df.columns
        ]

        return stock_data_df

    def get_data(
        self, start_date: str, end_date: str, col_rename: str, manual_loading=None
    ) -> pd.DataFrame:
        """Function to merge historical data from yahoo finance with manual uploads"""

        if manual_loading is not None and manual_loading.endswith(".csv"):
            manual_upload = self.__manual_upload(manual_loading, col_rename)
            logger.info("File loaded successfully.")
        else:
            raise ValueError("File path is either None or not a CSV file.")

        yf_data = self.__get_data_tickers_list(start_date=start_date, end_date=end_date)

        self.data = yf_data.join(manual_upload[col_rename])

        return self.data

    def __daily_basis(
        self, vol_future_ticker: str, vol_spot_ticker: str
    ) -> pd.DataFrame:
        """Calculates the daily basis for two indices to determine contango or backwardation"""

        self.data["basis"] = self.data[[vol_future_ticker, vol_spot_ticker]].apply(
            lambda x: (x[0] / x[1]) - 1, axis=1
        )

        return self.data

    def __lsv_signals(
        self,
        long_vix_asset: str,
        short_vix_asset: str,
        future_index_ticker: str,
        spot_index_ticker: str,
    ) -> pd.DataFrame:
        """Generating the signals for the Long-Short Strategy"""

        # Initialise signals dictionary with the keys based on asset names
        asset_signals = [
            f"{asset.lower()}_{signal_type}_signal"
            for signal_type in ["sell", "buy"]
            for asset in [long_vix_asset, short_vix_asset]
        ]
        signals = {signal: [] for signal in asset_signals}

        # Track the position of each asset
        positions = {"long_vix_asset": False, "short_vix_asset": False}

        # Column names for asset open prices
        long_vix_asset_open = f"{long_vix_asset.lower()}_open"
        short_vix_asset_open = f"{short_vix_asset.lower()}_open"

        df = self.__daily_basis(
            vol_future_ticker=f"{future_index_ticker.lower()}_open",
            vol_spot_ticker=f"{spot_index_ticker.lower()}_open",
        )

        for index in range(len(df)):
            # Check for negative basis (buy LONG_VIX_ASSET condition)
            if df["basis"][index] < 0:
                if not positions["long_vix_asset"]:
                    # If neither is long, open LONG_VIX_asset
                    if not positions["short_vix_asset"]:
                        signals[f"{long_vix_asset.lower()}_buy_signal"].append(
                            df.iloc[index][long_vix_asset_open]
                        )
                    else:
                        # If SHORT_VIX_ASSET is open, close it and open position in LONG_VIX_ASSET
                        signals[f"{short_vix_asset.lower()}_sell_signal"].append(
                            df.iloc[index][short_vix_asset_open]
                        )
                        signals[f"{long_vix_asset.lower()}_buy_signal"].append(
                            df.iloc[index][long_vix_asset_open]
                        )
                        positions["short_vix_asset"] = False

                    positions["long_vix_asset"] = True

                else:
                    # Maintain LONG_VIX_ASSET, no new signals
                    signals[f"{long_vix_asset.lower()}_buy_signal"].append(np.nan)

            else:
                # Check for positive basis
                if not positions["short_vix_asset"]:
                    if not positions["long_vix_asset"]:
                        signals[f"{short_vix_asset.lower()}_buy_signal"].append(
                            df.iloc[index][short_vix_asset_open]
                        )
                    else:
                        # If LONG_VIX_ASSET is open, close it and open position in SHORT_VIX_ASSET
                        signals[f"{long_vix_asset.lower()}_sell_signal"].append(
                            df.iloc[index][long_vix_asset_open]
                        )
                        signals[f"{short_vix_asset.lower()}_buy_signal"].append(
                            df.iloc[index][short_vix_asset_open]
                        )
                        positions["long_vix_asset"] = False

                    positions["short_vix_asset"] = True

                else:
                    # Maintain SHORT_VIX_ASSET, no new signals
                    signals[f"{short_vix_asset.lower()}_buy_signal"].append(np.nan)

            # Append NaNs for unused signals in each step
            for key, value in signals.items():
                if len(value) < index + 1:
                    signals[key].append(np.nan)

        # Create DataFrane with signals
        res = pd.DataFrame(signals, index=df.index)

        return res

    def lsv_strategy(
        self,
        intial_capital: float,
        long_vix_asset: str,
        short_vix_asset: str,
        future_index_ticker: str,
        spot_index_ticker: str,
    ) -> pd.DataFrame:
        """Simulate LSV trading strategy based on buy and sell signals in the DataFrame"""

        # Loading the signals dataframe
        signals_df = self.__lsv_signals(
            long_vix_asset=long_vix_asset,
            short_vix_asset=short_vix_asset,
            future_index_ticker=future_index_ticker,
            spot_index_ticker=spot_index_ticker,
        )

        # Initial values
        available_cash = intial_capital
        max_holding = 0
        current_asset = None
        sale_proceeds = 0.00
        holdings_history, cash_history, asset_history = (
            [],
            [],
            [],
        )

        # Execute first day trade from dataframe
        first_trade_dict = {
            key: value
            for key, value in signals_df.iloc[0].to_dict().items()
            if not np.isnan(value)
        }

        first_trade_key = list(first_trade_dict)[0]
        max_holding = (
            math.floor(available_cash / first_trade_dict[first_trade_key] * 100) / 100
        )
        available_cash -= max_holding * first_trade_dict[first_trade_key]
        current_asset = first_trade_key[:4]

        holdings_history.append(max_holding)
        cash_history.append(available_cash)
        asset_history.append(current_asset)

        for index in range(1, len(signals_df)):
            # Convert each row into a dictionary object
            execude_trades = {
                key: value
                for key, value in signals_df.iloc[index].to_dict().items()
                if not np.isnan(value)
            }

            # Non-empty dictionary means trade signal available
            if execude_trades:
                for signal, open_price in execude_trades.items():
                    # Sell current asset SHORT_VIX_ASSET or LONG_VIX_ASSET
                    if (short_vix_asset or long_vix_asset) and "sell" in signal:
                        sale_proceeds += max_holding * open_price
                        max_holding = 0
                        available_cash += sale_proceeds
                        sale_proceeds = 0.00

                    # Buy LONG_VIX_ASSET or SHORT_VIX_ASSET - counter trade
                    else:
                        max_holding = (
                            math.floor((available_cash / open_price) * 100) / 100
                        )
                        available_cash -= max_holding * open_price
                        current_asset = signal[:4]

                holdings_history.append(max_holding)
                cash_history.append(available_cash)
                asset_history.append(current_asset)

            # Empty dictionary, hence no trade for the trading day
            else:
                holdings_history.append(max_holding)
                cash_history.append(available_cash)
                asset_history.append(current_asset)

        res = pd.DataFrame(
            list(zip(asset_history, holdings_history, cash_history)),
            index=signals_df.index,
            columns=[
                "asset_history",
                "holding_quantity",
                "available_cash",
            ],
        )

        res["asset_close_price"] = res.apply(
            lambda x: self.data.loc[x.name][f"{x["asset_history"]}_close"], axis=1
        )
        res["asset_value"] = res["asset_close_price"] * res["holding_quantity"]
        res["portfolio_value"] = res["asset_value"] + res["available_cash"]
        res["portfolio_returns"] = res["portfolio_value"].pct_change()
        res["portfolio_cumulative_returns"] = (
            1 + res["portfolio_returns"]
        ).cumprod() - 1

        return res

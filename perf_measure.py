"""
The performance metrics class evaluates the performance of strategies that was
implemented in the TradingVolatility class. 

The class computes the Key Performance Indicators (KPIs) for each strategy,
such as the Geometric Return, Sharpe Ratio, Calmer Ration and other relevant metrics.
"""

import pandas as pd
import numpy as np


class PerformanceMetrics:
    """
    The aim is to provide insights into the effectiveness and risk-adjusted returns of
    the volatility trading strategies.
    """

    def __init__(
        self, df: pd.DataFrame, portfolio_value_col_name: str, index_col_name: str
    ):
        self.df = df
        self.portfolio_value_col_name = portfolio_value_col_name
        self.index_col_name = index_col_name

    def _year_start_helper(self, series) -> list[str]:

        tmp = series.copy().reset_index()
        res = (
            tmp.groupby(tmp[self.index_col_name].dt.year)[self.index_col_name]
            .min()
            .tolist()
        )

        return res[1:]

    def _year_end_helper(self, series) -> list[str]:

        tmp = series.copy().reset_index()
        res = (
            tmp.groupby(tmp[self.index_col_name].dt.year)[self.index_col_name]
            .max()
            .tolist()
        )

        return res[1:-1]

    def average_annulised_geometric_return(self) -> float:
        """
        Non-risk adjusted return - For GeRs, it will be considered between
        beginning of each year portfolio value and end of year value
        """

        tmp = self.df[self.portfolio_value_col_name].copy()
        year_start = self._year_start_helper(tmp)
        year_end = self._year_end_helper(tmp)

        tmp = tmp[tmp.index.isin(year_start) | tmp.index.isin(year_end)][:-1].to_frame()

        start_pv = []
        end_pv = []

        for date in tmp.index:
            if date.month == 1:
                start_pv.append(tmp.loc[date][0])
            else:
                end_pv.append(tmp.loc[date][0])

        res = pd.DataFrame(index=range(2012, 2020))
        res[["start_pv", "end_pv"]] = pd.Series([start_pv, end_pv])
        res["log_return"] = res.apply(
            lambda x: np.log(x["end_pv"] / x["start_pv"]), axis=1
        )

        ger = res["log_return"].sum() / len(res)

        return ger

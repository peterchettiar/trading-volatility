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

    def average_annual_geometric_return(self, portfolio_value: pd.Series) -> float:
        """
        Non-risk adjusted return - For GeRs, it will be considered between
        beginning of each year portfolio value and end of year value
        """

        tmp = portfolio_value.copy()

        year_start = tmp.groupby(tmp.index.year).agg(lambda x: x.index.min()).tolist()
        year_end = tmp.groupby(tmp.index.year).agg(lambda x: x.index.max()).tolist()

        res = pd.DataFrame(
            data=[
                {
                    "YEAR_START": s_date,
                    "PV_START": tmp.loc[s_date],
                    "YEAR_END": e_date,
                    "PV_END": tmp.loc[e_date],
                }
                for s_date, e_date in zip(year_start, year_end)
            ]
        )

        res["log_return"] = res.apply(
            lambda x: np.log(x["PV_END"] / x["PV_START"]), axis=1
        )

        ger = res["log_return"].sum() / len(res)

        return ger

    def annualised_downside_vol(
        self, portfolio_return: pd.Series, mar: float = 0
    ) -> float:
        """
        Measuring the volatility of negative returns (i.e. returns that are below
        a minimum acceptable return - in our case zero), on an annualised basis.
        """

        tmp = portfolio_return.copy()

        annual_dow_vol = np.sqrt(
            tmp[tmp < mar].map(lambda x: x**2).sum() / len(tmp)
        ) * np.sqrt(252)

        return annual_dow_vol

    def annualised_vol(self, portfolio_return: pd.Series) -> float:
        """
        Measuring the annualised total standard deviation of portfolio returns.
        """

        tmp = portfolio_return.copy()

        return tmp.std() * np.sqrt(252)

    def maximum_drawdown(self, portfolio_value: pd.Series) -> float:
        """
        Maximum drawdown is the maximum observed loss from a peak to a trough of a portfolio,
        before a new peak is attained.
        """

        tmp = portfolio_value.copy()

        # Calculate the cumulative maximum
        cumulative_max = tmp.cummax()

        # Calculate the drawdown
        drawdown = (tmp - cumulative_max) / cumulative_max

        # Return the maximum drawdown
        return drawdown.min()

    def annualised_sharpe_ratio(
        self, portfolio_returns: pd.Series, risk_free_annual: float = 0.04
    ) -> float:
        """
        Excess return of portfolio per unit of total risk (i.e. standard deviation)
        """

        returns = portfolio_returns.copy()

        # Converting annual risk free to daily
        risk_free_daily = (1 + risk_free_annual) ** (1 / 252) - 1

        # Calculate excess returns
        excess_returns = returns - risk_free_daily

        daily_sharpe = excess_returns.mean() / returns.std()

        annualised_sharpe = daily_sharpe * np.sqrt(252)

        return annualised_sharpe

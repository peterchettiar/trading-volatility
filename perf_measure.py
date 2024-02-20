import pandas as pd
import numpy as np

class performance_metrics():

    def __init__(self, df: pd.DataFrame(), portfolio_value_col_name: str, index_col_name: str):
        self.df = df
        self.portfolio_value_col_name = portfolio_value_col_name
        self.index_col_name = index_col_name
    
    def _year_start_helper(self, series) -> list[str]:

        tmp = series.copy().reset_index()
        res = tmp.groupby(tmp[self.index_col_name].dt.year)[self.index_col_name].min().tolist()

        return res[1:]

    def _year_end_helper(self, series) -> list[str]:

        tmp = series.copy().reset_index()
        res = tmp.groupby(tmp[self.index_col_name].dt.year)[self.index_col_name].max().tolist()

        return res[1:-1]

    def GeR_metric(self) -> float:

        tmp = self.df[self.portfolio_value_col_name].copy()
        year_start = self._year_start_helper(tmp)
        year_end = self._year_end_helper(tmp)

        tmp = tmp[tmp.index.isin(year_start) | tmp.index.isin(year_end)][:-1].to_frame()

        start_PV = []
        end_PV = []

        for date in tmp.index:
            if date.month == 1:
                start_PV.append(tmp.loc[date][0])
            else:
                end_PV.append(tmp.loc[date][0])

        res = pd.DataFrame(index=range(2012,2020))
        res[["start_pv","end_pv"]] = pd.Series([start_PV,end_PV])
        res["log_return"] = res.apply(lambda x : np.log(x["end_pv"] / x["start_pv"]), axis=1)

        GeR = res["log_return"].sum() / len(res)

        return GeR
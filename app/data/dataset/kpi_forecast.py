import numpy as np
import pandas as pd
from app.data.database import get_engine, canonical_rev_query
from app.core.config import settings

class KPIDataset():
    def __init__(self):
        self.engine = get_engine()

        self.selects = f"""
        SELECT
            ams.invoice_date,
            amsl.nepa_cogs_price, amsl.discount, amsl.price_unit
        """
        self.dates = ["2023-12-01", "2024-12-01", "2025-12-01", "2026-09-13"]

        self._extract_data()
        self._feature_engineering()

    def _extract_data(self):
        chunks = []
        for i in range(len(self.dates)-1):
            query = canonical_rev_query(self.selects, start_date= self.dates[i], end_date=self.dates[i+1])
            print("connecting to nepa db")
            for chunk in pd.read_sql(query, self.engine, chunksize=500000):
                chunks.append(chunk)
                print(f"Loaded chunk with {len(chunk)} rows")

        self.engine.dispose()

        df_kpi_forecasting: pd.DataFrame = pd.concat(chunks, ignore_index=True)

        self.df_kpi_forecasting = df_kpi_forecasting.groupby(["invoice_date"], as_index=False).agg({
            "nepa_cogs_price": ["sum"],
            "price_unit": ["sum"], 
            "revenue_signed": ["sum"], 
            "qty_signed": ["sum"],
            "discount" : ["sum"]
        })

        self.df_kpi_forecasting.columns = [
            f"{col[0]}_{col[1]}" if col[1] else col[0] 
            for col in self.df_kpi_forecasting.columns
        ]

    def _feature_engineering(self):
        df_explore = self.df_kpi_forecasting.sort_values(by="invoice_date").reset_index(drop=True)

        full_date_range = pd.date_range(
            start=df_explore["invoice_date"].min(),
            end=df_explore["invoice_date"].max(),
            freq="D"
        )

        df_explore = (
            df_explore.set_index('invoice_date')
            .reindex(full_date_range)
            .ffill()
            .rename_axis("invoice_date")
            # .reset_index()
        )

        # date based features and target creation
        # creating target
        df_explore = df_explore.sort_values(by="invoice_date")

        # revenue target
        df_explore["target"] = df_explore["revenue_signed_sum"].shift(-1)
        df_explore["target_diff"] = (df_explore["target"]-df_explore["revenue_signed_sum"])

        # qty target
        df_explore["target_qty"] = df_explore["qty_signed_sum"].shift(-1)
        df_explore["target_qty_diff"] = (df_explore["target_qty"]-df_explore["qty_signed_sum"])

        # date features
        df_explore["invoice_date"] = df_explore.index

        df_explore["month"] = df_explore["invoice_date"].dt.month_name()
        df_explore["day_of_week"] = df_explore["invoice_date"].dt.day_name()
        # df_explore = df_explore[df_explore["day_of_week"] != "sunday"]

        # month features
        df_explore["month"] = df_explore["invoice_date"].dt.month
        df_explore["month_tgt_enc"] =  df_explore.groupby("month")["target"].transform(lambda x: x.shift(1).expanding(min_periods=1).mean())

        # week of day features
        df_explore["dow_tgt_enc"] =  df_explore.groupby("day_of_week")["target"].transform(lambda x: x.shift(1).expanding(min_periods=1).mean())
        df_explore["day_of_week_sma7W"] = (df_explore.groupby("day_of_week"))["target"].transform(lambda x: x.shift(1).rolling(window=7, min_periods=1).mean())

        # SMA features
        cols = ["qty_signed_sum", "revenue_signed_sum"]
        prefix_map = {
            "nepa_cogs_price_sum" : "cogs",
            "revenue_signed_sum" : "rev",
            "qty_signed_sum" : "qty", 
            "standard_price_sum": "sp_sum",
            "price_unit_sum": "pu_sum"
        }
        sma_duration = [7]
        for col in cols:
            prefix = prefix_map.get(col,col)
            for i in sma_duration:
                df_explore[f"{prefix}_{i}d_ma"] = (df_explore[col].shift(1).rolling(window=i, min_periods=1).mean())


        # LAG features
        from statsmodels.graphics.tsaplots import pacf
        cols = ["qty_signed_sum", "revenue_signed_sum"]
        prefix_map = {
            "nepa_cogs_price_sum" : "cogs",
            "revenue_signed_sum" : "rev",
            "qty_signed_sum" : "qty", 
            "standard_price_sum": "sp_sum",
            "price_unit_sum": "pu_sum"
        }
        for col in cols:
            pacf_vals, confint = pacf(
                df_explore[col],
                nlags=32,
                method="ywm",
                alpha=0.005
            )

            pacf_df = pd.DataFrame({
                "lag": range(len(pacf_vals)),
                "pacf": pacf_vals,
                "lower_ci": confint[:, 0],
                "upper_ci": confint[:, 1]
            })

            pacf_df["significant"] = (
                (pacf_df["lower_ci"] > 0) |
                (pacf_df["upper_ci"] < 0)
            )

            is_valid_lag = pacf_df["significant"]
            lag_duration = pacf_df.loc[is_valid_lag, "lag"].tolist()
            
            prefix = prefix_map.get(col,col)
            for i in lag_duration:
                if i+1 > 6:
                    df_explore[f"{prefix}_lag_{i+1}"] = df_explore[col].shift(i)

        keep_ma = ["discount_sum_90d_ma", "rev_7d_ma", "qty_7d_ma" ]
        keep_agg = ["discount_sum", "revenue_signed_sum", "qty_signed_sum"]

        cols_to_drop_ma = [
            col for col in df_explore.columns if (col.endswith("_ma")) and col not in keep_ma
        ]

        cols_to_drop_agg = [
            col for col in df_explore.columns if (col.endswith("_sum") or col.endswith("_mean") or col.endswith("_<lambda_0>")) and col not in keep_agg
        ]
        df_explore.drop(columns=cols_to_drop_ma, inplace=True)
        df_explore.drop(columns=cols_to_drop_agg, inplace=True)
        self.df_kpi_forecasting = df_explore
        
dataset: pd.DataFrame = KPIDataset().df_kpi_forecasting
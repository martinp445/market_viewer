import numpy as np
import pandas as pd


class IndicatorCalculator:

    @staticmethod
    def calculate(df):

        df = df.copy()

        # Ensure numeric data
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        #
        # EMA
        #

        df["EMA20"] = (
            df["Close"]
            .ewm(span=20, adjust=False)
            .mean()
        )

        df["EMA50"] = (
            df["Close"]
            .ewm(span=50, adjust=False)
            .mean()
        )

        df["EMA200"] = (
            df["Close"]
            .ewm(span=200, adjust=False)
            .mean()
        )

        #
        # RSI(14)
        #

        delta = df["Close"].diff()

        gain = delta.where(
            delta > 0,
            0.0
        )

        loss = -delta.where(
            delta < 0,
            0.0
        )

        avg_gain = gain.rolling(
            window=14,
            min_periods=14
        ).mean()

        avg_loss = loss.rolling(
            window=14,
            min_periods=14
        ).mean()

        rs = avg_gain / avg_loss

        df["RSI"] = (
            100
            - (100 / (1 + rs))
        )

        #
        # ATR(14)
        #

        high_low = (
            df["High"] - df["Low"]
        )

        high_close = np.abs(
            df["High"]
            - df["Close"].shift()
        )

        low_close = np.abs(
            df["Low"]
            - df["Close"].shift()
        )

        true_range = pd.concat(
            [
                high_low,
                high_close,
                low_close
            ],
            axis=1
        ).max(axis=1)

        df["ATR"] = (
            true_range
            .rolling(14)
            .mean()
        )

        #
        # Volume indicators
        #

        df["VolumeAvg"] = (
            df["Volume"]
            .rolling(20)
            .mean()
        )

        df["RelVolume"] = (
            df["Volume"]
            / df["VolumeAvg"]
        )

        #
        # Daily return
        #

        df["DailyReturn"] = (
            df["Close"]
            .pct_change()
            * 100
        )

        #
        # 5 day performance
        #

        df["Perf5D"] = (
            (
                df["Close"]
                /
                df["Close"].shift(5)
            )
            - 1
        ) * 100

        #
        # Cleanup
        #

        df.replace(
            [np.inf, -np.inf],
            np.nan,
            inplace=True
        )

        return df
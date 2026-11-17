import pandas as pd
import yfinance as yf


class MarketDataService:

    def get_stock_data(self, symbol: str):
        try:
            df = yf.download(
                symbol,
                period="1y",
                interval="1d",
                auto_adjust=True,
                progress=False
            )

            if df is None or df.empty:
                return None

            # Fix for newer yfinance versions
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Ensure we only keep required columns
            expected = [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume"
            ]

            missing = [
                col
                for col in expected
                if col not in df.columns
            ]

            if missing:
                print(
                    f"{symbol}: Missing columns {missing}"
                )
                return None

            # Convert everything to numeric
            for col in expected:
                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

            df = df.dropna()

            return df

        except Exception as e:
            print(
                f"Error loading {symbol}: {e}"
            )
            return None
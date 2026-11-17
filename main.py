import sys

from PySide6.QtWidgets import (
    QApplication,
    QTableWidgetItem,
)

from ui import MainWindow
from data import MarketDataService
from indicators import IndicatorCalculator
from scoring import ScoringEngine


WATCHLIST = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMD",
    "META",
    "AMZN",
    "GOOGL",
    "TSLA",
    "PLTR",
]


def build_stock_row(symbol, df):

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    score = ScoringEngine.calculate_score(df)
    trend = ScoringEngine.trend_label(df)

    daily_change = (
        (
            float(latest["Close"])
            - float(previous["Close"])
        )
        / float(previous["Close"])
    ) * 100

    return [
        symbol,
        round(float(latest["Close"]), 2),
        round(daily_change, 2),
        round(float(latest["RSI"]), 1),
        round(float(latest["RelVolume"]), 2),
        round(score, 2),
        trend,
    ]


def build_market_rows():

    service = MarketDataService()

    rows = []
    stock_data = {}

    for symbol in WATCHLIST:

        try:

            print(f"Loading {symbol}")

            df = service.get_stock_data(symbol)

            if df is None:
                continue

            df = IndicatorCalculator.calculate(df)

            stock_data[symbol] = df

            row = build_stock_row(
                symbol,
                df,
            )

            rows.append(row)

        except Exception as ex:

            print(
                f"Error loading {symbol}: {ex}"
            )

    rows.sort(
        key=lambda row: row[5],
        reverse=True,
    )

    return rows, stock_data


def add_symbol(window, symbol):

    try:

        symbol = symbol.upper().strip()

        if not symbol:
            return

        #
        # already loaded
        #

        if symbol in window.stock_data:

            print(
                f"{symbol} already loaded"
            )

            window.show_chart(symbol)

            return

        service = MarketDataService()

        print(
            f"Loading new symbol: {symbol}"
        )

        df = service.get_stock_data(symbol)

        if df is None:

            print(
                f"Unable to load {symbol}"
            )

            return

        df = IndicatorCalculator.calculate(df)

        window.stock_data[symbol] = df

        row_data = build_stock_row(
            symbol,
            df,
        )

        window.add_row(row_data)

        window.show_chart(symbol)

    except Exception as ex:

        print(
            f"Failed adding {symbol}: {ex}"
        )


def refresh_all(window):

    print("Refreshing market data...")

    rows, stock_data = build_market_rows()

    window.stock_data = stock_data

    window.table.setRowCount(0)

    window.populate(rows)

    if rows:

        window.show_chart(
            rows[0][0]
        )


def main():

    app = QApplication(sys.argv)

    window = MainWindow()

    #
    # INITIAL LOAD
    #

    rows, stock_data = build_market_rows()

    window.stock_data = stock_data

    window.populate(rows)

    #
    # SEARCH CALLBACK
    #

    window.add_symbol_callback = (
        lambda symbol:
        add_symbol(
            window,
            symbol
        )
    )

    #
    # REFRESH BUTTON
    #

    window.refresh_btn.clicked.connect(
        lambda:
        refresh_all(window)
    )

    #
    # SHOW FIRST STOCK
    #

    if rows:

        first_symbol = rows[0][0]

        window.show_chart(
            first_symbol
        )

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
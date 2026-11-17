from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QPushButton,
    QLineEdit,
    QHeaderView,
)

from PySide6.QtCore import Qt

import pyqtgraph as pg


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.stock_data = {}

        # callback assigned from main.py
        self.add_symbol_callback = None

        self.setWindowTitle("Market Viewer")
        self.resize(1400, 900)

        self.build_ui()

    def build_ui(self):

        layout = QHBoxLayout(self)

        #
        # LEFT PANEL
        #

        left_panel = QVBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText(
            "Type symbol and press ENTER (NVDA, AAPL, TSLA...)"
        )

        self.search.returnPressed.connect(
            self.search_enter_pressed
        )

        self.refresh_btn = QPushButton(
            "Refresh"
        )

        self.table = QTableWidget()

        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels([
            "Symbol",
            "Price",
            "1D %",
            "RSI",
            "Rel Vol",
            "Score",
            "Trend"
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setSortingEnabled(True)

        self.table.cellClicked.connect(
            self.row_selected
        )

        left_panel.addWidget(self.search)
        left_panel.addWidget(self.refresh_btn)
        left_panel.addWidget(self.table)

        #
        # RIGHT PANEL
        #

        right_panel = QVBoxLayout()

        self.symbol_label = QLabel(
            "Select a stock"
        )

        self.symbol_label.setAlignment(
            Qt.AlignCenter
        )

        self.symbol_label.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
            """
        )

        self.chart = pg.PlotWidget()

        self.chart.setBackground("#111111")

        self.chart.showGrid(
            x=True,
            y=True,
            alpha=0.3
        )

        self.chart.setLabel(
            "left",
            "Price"
        )

        self.chart.setLabel(
            "bottom",
            "Days"
        )

        right_panel.addWidget(
            self.symbol_label
        )

        right_panel.addWidget(
            self.chart
        )

        layout.addLayout(left_panel, 3)
        layout.addLayout(right_panel, 2)

    #
    # SEARCH
    #

    def search_enter_pressed(self):

        symbol = self.search.text().strip().upper()

        if not symbol:
            return

        if self.add_symbol_callback:
            self.add_symbol_callback(symbol)

        self.search.clear()

    #
    # TABLE
    #

    def populate(self, rows):

        self.table.setRowCount(len(rows))

        for row_idx, row in enumerate(rows):

            for col_idx, value in enumerate(row):

                self.table.setItem(
                    row_idx,
                    col_idx,
                    QTableWidgetItem(
                        str(value)
                    )
                )

    def add_row(self, row_data):

        row = self.table.rowCount()

        self.table.insertRow(row)

        for col, value in enumerate(row_data):

            self.table.setItem(
                row,
                col,
                QTableWidgetItem(
                    str(value)
                )
            )

    #
    # SELECTION
    #

    def row_selected(self, row, column):

        item = self.table.item(row, 0)

        if item is None:
            return

        symbol = item.text()

        self.show_chart(symbol)

    #
    # CHART
    #

    def show_chart(self, symbol):

        if symbol not in self.stock_data:
            return

        df = self.stock_data[symbol]

        self.symbol_label.setText(symbol)

        self.chart.clear()

        try:

            close = (
                df["Close"]
                .astype(float)
                .values
            )

            self.chart.plot(
                close,
                pen=pg.mkPen(
                    color="#FFFFFF",
                    width=2
                ),
                name="Close"
            )

            if "EMA20" in df.columns:

                self.chart.plot(
                    df["EMA20"]
                    .astype(float)
                    .values,
                    pen=pg.mkPen(
                        color="#FFD700",
                        width=1
                    )
                )

            if "EMA50" in df.columns:

                self.chart.plot(
                    df["EMA50"]
                    .astype(float)
                    .values,
                    pen=pg.mkPen(
                        color="#00E5FF",
                        width=1
                    )
                )

            if "EMA200" in df.columns:

                self.chart.plot(
                    df["EMA200"]
                    .astype(float)
                    .values,
                    pen=pg.mkPen(
                        color="#FF00FF",
                        width=2
                    )
                )

            self.chart.enableAutoRange()

        except Exception as e:

            print(
                f"Chart error for {symbol}: {e}"
            )
class ScoringEngine:

    @staticmethod
    def calculate_score(df):

        latest = df.iloc[-1]

        score = 0

        trend = 0

        if latest["Close"] > latest["EMA20"]:
            trend += 15

        if latest["Close"] > latest["EMA50"]:
            trend += 15

        if latest["Close"] > latest["EMA200"]:
            trend += 10

        score += trend

        rsi = latest["RSI"]

        momentum = 0

        if 50 <= rsi <= 70:
            momentum += 30

        elif 40 <= rsi < 50:
            momentum += 20

        elif 70 < rsi <= 80:
            momentum += 15

        score += momentum

        rel_volume = latest["RelVolume"]

        volume_score = min(rel_volume * 10, 20)

        score += volume_score

        atr_percent = (
            latest["ATR"] / latest["Close"]
        ) * 100

        volatility_score = 10

        if atr_percent > 5:
            volatility_score = 5

        score += volatility_score

        return round(min(score, 100), 2)

    @staticmethod
    def trend_label(df):

        latest = df.iloc[-1]

        if (
            latest["Close"] > latest["EMA20"]
            and latest["Close"] > latest["EMA50"]
        ):
            return "Bullish"

        if (
            latest["Close"] < latest["EMA20"]
            and latest["Close"] < latest["EMA50"]
        ):
            return "Bearish"

        return "Neutral"
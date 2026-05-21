import yfinance as yf
import pandas as pd
from smartmoneyconcepts import smc

df_ltf = yf.download("EURUSD=X", period="5d", interval="5m")
df_ltf.columns = ["Open", "High", "Low", "Close", "Volume"]
df_ltf.dropna(inplace=True)

fvg = smc.fvg(df_ltf)
swings = smc.swing_highs_lows(df_ltf, swing_length=5)

print("FVG найдено строк:", len(fvg))
print(fvg.tail(3))

print("\nПоследние свинг-точки:")
print(swings.tail(5))

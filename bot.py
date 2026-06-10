import ccxt
import pandas_ta as ta
import pandas as pd
import time
import requests
import logging
import yfinance as yf
from datetime import datetime, timezone, timedelta

# --- LOGGING AYARI ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- BİLGİLERİN ---
TOKEN = "8607888019:AAH_9KT13bI_K3JjdSi52o_DTNxL2nWkRKc"
CHAT_ID = "6220442563"
SYMBOL = 'PAXG/USDT'
CHECK_INTERVAL = 10

TZ_TR = timezone(timedelta(hours=3))

exchange = ccxt.kucoin({
    'enableRateLimit': True,
    'timeout': 30000,
})


def now_tr():
    return datetime.now(TZ_TR)


def is_trading_hour():
    h = now_tr().hour
    return 8 <= h <= 23


def send_telegram_msg(text):
    for attempt in range(3):
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            payload = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'}
            response = requests.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Telegram mesajı gönderildi.")
                return True
        except Exception as e:
            logger.error(f"❌ Mesaj Hatası (Deneme {attempt+1}/3): {e}")
            time.sleep(2)
    return False


def get_paxg_rsi():
    df_5m = pd.DataFrame(
        exchange.fetch_ohlcv(SYMBOL, '5m', limit=100),
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
    )
    df_15m = pd.DataFrame(
        exchange.fetch_ohlcv(SYMBOL, '15m', limit=100),
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
    )
    df_5m['rsi'] = ta.rsi(df_5m['close'], length=14)
    df_15m['rsi'] = ta.rsi(df_15m['close'], length=14)
    return round(df_5m['rsi'].iloc[-1], 2), round(df_15m['rsi'].iloc[-1], 2)


def get_xau_vwap():
    df = yf.download('GC=F', period='1d', interval='5m', progress=False)
    if df.empty:
        return None, None
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df['tp']  = (df['High'] + df['Low'] + df['Close']) / 3
    df['tpv'] = df['tp'] * df['Volume']
    vwap = df['tpv'].cumsum() / df['Volume'].cumsum()
    xau_price = round(float(df['Close'].iloc[-1]), 2)
    vwap_val  = round(float(vwap.iloc[-1]), 2)
    return vwap_val, xau_price


def run_bot():
    logger.info("🚀 XAU/USD VWAP + RSI BOT BAŞLATILDI")
    send_telegram_msg(
        f"🤖 <b>XAU VWAP + RSI Bot Başlatıldı!</b>\n"
        f"📊 RSI: PAXG/USDT (KuCoin)\n"
        f"📊 VWAP: XAU/USD (Yahoo Finance)\n"
        f"⏱ Timeframe: 5m + 15m\n"
        f"📈 RSI 30/70 + VWAP filtresi\n"
        f"🕐 Aktif: 08:00 - 23:59 (Türkiye)\n"
        f"🕐 {now_tr().strftime('%H:%M:%S')}"
    )

    last_alert = None
    consecutive_errors = 0
    MAX_ERRORS = 10

    while True:
        try:
            tr_time = now_tr().strftime('%H:%M')

            if is_trading_hour():
                rsi_5m, rsi_15m = get_paxg_rsi()
                vwap, xau_price = get_xau_vwap()

                if vwap and xau_price:
                    vwap_bull = xau_price < vwap
                    vwap_bear = xau_price > vwap
                else:
                    vwap_bull = False
                    vwap_bear = False

                logger.info(
                    f"RSI 5m: {rsi_5m} | RSI 15m: {rsi_15m} | "
                    f"XAU: {xau_price} | VWAP: {vwap}"
                )

                # GÜÇLÜ ALIŞ
                if rsi_5m <= 30 and rsi_15m <= 35 and vwap_bull and last_alert != "buy":
                    msg = (
                        f"🟢🟢 <b>GÜÇLÜ ALIŞ SİNYALİ — XAU/USD</b>\n"
                        f"📊 VWAP altında ✅\n"
                        f"📉 RSI 5m: {rsi_5m} | RSI 15m: {rsi_15m}\n"
                        f"🕐 {tr_time}"
                    )
                    send_telegram_msg(msg)
                    last_alert = "buy"

                # GÜÇLÜ SATIŞ
                elif rsi_5m >= 70 and rsi_15m >= 65 and vwap_bear and last_alert != "sell":
                    msg = (
                        f"🔴🔴 <b>GÜÇLÜ SATIŞ SİNYALİ — XAU/USD</b>\n"
                        f"📊 VWAP üstünde ✅\n"
                        f"📈 RSI 5m: {rsi_5m} | RSI 15m: {rsi_15m}\n"
                        f"🕐 {tr_time}"
                    )
                    send_telegram_msg(msg)
                    last_alert = "sell"

                # Nötr bölge — sıfırla
                elif 45 < rsi_5m < 55:
                    last_alert = None

            else:
                if now_tr().second % 30 == 0:
                    logger.info(f"💤 Saat 08:00'i bekliyor...")

            consecutive_errors = 0
            time.sleep(CHECK_INTERVAL)

        except ccxt.NetworkError as e:
            consecutive_errors += 1
            logger.error(f"🌐 Ağ Hatası ({consecutive_errors}/{MAX_ERRORS}): {e}")
            time.sleep(30)
        except ccxt.ExchangeError as e:
            consecutive_errors += 1
            logger.error(f"🏦 Borsa Hatası ({consecutive_errors}/{MAX_ERRORS}): {e}")
            time.sleep(60)
        except Exception as e:
            consecutive_errors += 1
            logger.error(f"⚠️ Hata ({consecutive_errors}/{MAX_ERRORS}): {e}")
            time.sleep(10)

        if consecutive_errors >= MAX_ERRORS:
            send_telegram_msg(f"🚨 <b>BOT KRİTİK HATA!</b>\n{MAX_ERRORS} ardışık hata oluştu!")
            consecutive_errors = 0


if __name__ == "__main__":
    run_bot()

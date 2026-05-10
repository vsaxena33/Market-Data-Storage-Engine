# Market-Data-Storage-Engine

High-performance historical market data pipeline with multithreaded fetching, rate limiting, and parquet storage.

This project downloads historical OHLCV market data for thousands of symbols across multiple exchanges and stores them efficiently in Apache Parquet format for fast analytics, backtesting, and quantitative research.

---

# Features

- Download historical market data from FYERS
- Multi-exchange symbol support
- Multithreaded parallel data fetching
- Built-in API rate limiting
- Automatic parquet storage
- Duplicate timestamp removal
- Timezone conversion to IST
- Scalable architecture for large datasets

---

# Supported Exchanges

The project currently supports:

- NSE_CM
- NSE_FO
- NSE_CD
- NSE_COM
- BSE_CM
- BSE_FO
- MCX_COM

---

# Project Structure

```bash
market-data-storage-engine/
│
├── main.py
├── credentials.py
├── autoLogin.py
├── dataFile.py
├── fetchSymbol.py
├── historicalData.py
├── initializer.py
├── main.py
├── rateLimiter.py
├── symbolMaster.py
├── README.md
├── LICENSE
└── requirements.txt
```

---

# Install Dependencies

``` Bash
pip install -r requirements.txt
```

---

# Running Progeam

``` Bash
python main.py
```

---

# Output

Downloaded market data is stored inside:

``` Bash
parquet_data/
```

Each symbol gets its own parquet file.

Example:

``` Bash
NSE_RELIANCE_EQ.parquet
NSE_TCS_EQ.parquet
```

---

# Data Format

Each parquet file contains:

| Column | Description   |
| ------ | ------------- |
| open   | Opening price |
| high   | Highest price |
| low    | Lowest price  |
| close  | Closing price |
| volume | Trade volume  |

Index:

- Datetime (IST timezone)

---

# Architecture Overview

The pipeline works in the following stages:

1. Download symbol master files
2. Merge exchange symbol data
3. Extract unique symbols
4. Fetch historical OHLCV data
5. Apply rate limiting
6. Store cleaned data into parquet files

---

# Performance Features
## Multithreading

Uses ```ThreadPoolExecutor``` for parallel downloads.

## Rate Limiting

Prevents exceeding FYERS API limits:

* Max 8 requests/second
* Max 180 requests/minute

## Efficient Storage

Uses Apache Parquet format for:

* Faster reads
* Smaller file sizes
* Better analytics performance

---

# Disclaimer

This project is for educational and research purposes only.

Use responsibly and ensure compliance with FYERS API terms and exchange regulations.

---

# Author

Vaibhav Saxena

---

# License

MIT License

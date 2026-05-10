# Market Data Engine

High-performance historical market data ingestion and storage pipeline for quantitative research, backtesting, and systematic trading.

This project downloads historical OHLCV market data from FYERS across multiple exchanges, processes it using a multithreaded architecture with thread-safe rate limiting, and stores it efficiently in Apache Parquet format for fast analytics and scalable research workflows.

---

# 🎯 Motivation

Systematic trading strategies require large amounts of clean and structured historical market data for:

- Backtesting
- Quantitative research
- Signal generation
- Feature engineering
- Strategy validation
- Execution simulation

This project was built to create a scalable local market-data infrastructure capable of storing high-frequency OHLCV data efficiently while respecting broker API constraints and handling real-world market data issues such as sparse option-chain candles and illiquid contracts.

---

# ⚡ Features

- Historical OHLCV market data ingestion from FYERS
- Multi-exchange symbol support
- Multithreaded parallel data fetching
- Thread-safe API rate limiting
- Incremental parquet updates
- Automatic duplicate timestamp removal
- Timezone conversion to IST
- Efficient Apache Parquet storage
- Handles sparse option-chain candles
- Scalable architecture for large datasets
- Fault-tolerant symbol-level exception handling

---

# 📈 Supported Exchanges

Currently supported exchanges:

- NSE_CM
- NSE_FO
- NSE_CD
- NSE_COM
- BSE_CM
- BSE_FO
- MCX_COM

---

# 🛠 Tech Stack

| Component | Technology |
|----------|-------------|
| Language | Python |
| Concurrency | ThreadPoolExecutor |
| Data Processing | Pandas |
| Storage | Apache Parquet |
| Serialization | PyArrow |
| Broker API | FYERS API |
| Rate Limiting | Thread-safe custom limiter |

---

# 📂 Project Structure

```bash
market-data-engine/
│
├── main.py
├── credentials.py
├── autoLogin.py
├── dataFile.py
├── fetchSymbol.py
├── historicalData.py
├── initializer.py
├── rateLimiter.py
├── symbolMaster.py
├── parquet_data/
├── README.md
├── LICENSE
└── requirements.txt
```

---

# 📦 Installation

## Clone the Repository

```bash
git clone https://github.com/your-username/market-data-engine.git
cd market-data-engine
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 API Setup

To run this project you need:
- A Fyers trading account
- API credentials
- Access token

Generate the access token using:

```bash
python autoLogin.py
```

> Note: Due to SEBI guidelines, a new access token must be generated daily.

Add your FYERS API credentials inside:

``` Bash
credentials.py
```

Example:

``` Bash
CLIENT_ID = "YOUR_CLIENT_ID"
SECRET_KEY = "YOUR_SECRET_KEY"
REDIRECT_URI = "YOUR_REDIRECT_URI"
```
---

# ▶️ Running Program

``` Bash
python main.py
```

---

# 📂 Data Storage

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

# 📊 Data Format

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

# 🧠 Architecture Overview

The pipeline works in the following stages:

1. Download symbol master files
2. Merge exchange symbol data
3. Extract unique symbols
4. Fetch historical OHLCV data
5. Apply rate limiting
6. Remove duplicate timestamps
7. Store cleaned data into parquet files

---

# 🚀 Performance Features
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
* Efficient columnar compression

---

# ⚠️ Disclaimer

This project is intended strictly for educational and research purposes.

Users are responsible for ensuring compliance with:

* FYERS API Terms of Service
* Exchange regulations
* SEBI guidelines
* Applicable financial market laws

---

# 👨‍💻 Author

Vaibhav Saxena

---

# 📜 License

MIT License

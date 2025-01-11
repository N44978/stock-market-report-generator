# stock-market-report-generator

# Usage: 

download the repo, then extract to designated folder. 

> Make sure you have these installed. "pip install requests pandas colorama python-dotenv tabulate"

> Run "python3 main.py" > Click 1. 


The script will create a raw CSV report, and a detailed more easy to read ascii report. 
Example: 
Title  │ Ticker   │ Impact   │ Sentiment   │ Summary |  Link     │ Published_At         │ Source             │

SENTIMENT DISTRIBUTION:

Bullish : ---------- (10)
Bearish : --- (3)
Neutral : ----------------------------------------------- (47)


Feel free to edit the article search terms. 

> [INFO] Fetching articles for: stock market
> [INFO] Fetching articles for: crypto
> [INFO] Fetching articles for: bitcoin
> [INFO] Fetching articles for: technology stocks
> [INFO] Fetching articles for: financial markets
> [INFO] Fetching articles for: energy sector
> [INFO] Fetching articles for: healthcare sector
> [INFO] Fetching articles for: consumer discretionary sector
> [INFO] Fetching articles for: industrial sector
> [INFO] Fetching articles for: materials sector
> [INFO] Fetching articles for: real estate market
> [INFO] Fetching articles for: utilities sector
> [INFO] Using output folder: ./reports_2025-01-11
> [SUCCESS] CSV report generated: ./reports_2025-01-11\market_report_2025-01-11.csv
> [SUCCESS] ASCII text report generated: ./reports_2025-01-11\market_report_2025-01-11.txt

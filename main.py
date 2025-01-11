import os
import sys
import requests
import pandas as pd
from datetime import datetime
from colorama import init, Fore, Style
from dotenv import load_dotenv
from tabulate import tabulate

init(autoreset=True)
load_dotenv()
NEWS_API_KEY = os.getenv("NEWSAPI_KEY", "")

STOCK_TICKERS = {
    "apple": "AAPL",
    "tesla": "TSLA",
    "microsoft": "MSFT",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "amazon": "AMZN",
    "meta": "META",
    "facebook": "META",
    "nvidia": "NVDA",
    "berkshire": "BRK.A",
}

CRYPTO_TICKERS = {
    "bitcoin": "BTC",
    "btc": "BTC",
    "ethereum": "ETH",
    "ether": "ETH",
    "dogecoin": "DOGE",
    "doge": "DOGE",
    "litecoin": "LTC",
    "xrp": "XRP",
    "ripple": "XRP",
    "solana": "SOL",
}
def log_colored_message(message, status="info"):
    if status == "info":
        print(Fore.CYAN + "[INFO] " + Style.RESET_ALL + message)
    elif status == "success":
        print(Fore.GREEN + "[SUCCESS] " + Style.RESET_ALL + message)
    elif status == "warning":
        print(Fore.YELLOW + "[WARNING] " + Style.RESET_ALL + message)
    elif status == "error":
        print(Fore.RED + "[ERROR] " + Style.RESET_ALL + message)
    else:
        print(message)

def get_top_headlines(query, language="en", page_size=10):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": language,
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY,
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        return articles
    except requests.exceptions.RequestException as e:
        log_colored_message(f"Failed to fetch articles for '{query}': {e}", "error")
        return []

def summarize_article(article):
    title = article.get("title", "No Title")
    description = article.get("description", "")
    return f"{title}. {description}"

def determine_impact(article, keywords):
    title = (article.get("title") or "").lower()
    description = (article.get("description") or "").lower()
    content = (article.get("content") or "").lower()
    
    text = " ".join([title, description, content])
    
    if any(keyword in text for keyword in keywords["crypto"]):
        return "Crypto"
    elif any(keyword in text for keyword in keywords["stocks"]):
        return "Stocks"
    else:
        return "General"

def determine_sentiment(text):
    bullish_words = ["rise", "rises", "soar", "soars", "gain", "gains", "bullish", "positive", "surge"]
    bearish_words = ["fall", "falls", "drop", "drops", "bearish", "negative", "plummet", "decline"]
    
    text_lower = text.lower()
    if any(word in text_lower for word in bullish_words):
        return "Bullish"
    elif any(word in text_lower for word in bearish_words):
        return "Bearish"
    else:
        return "Neutral"


def guess_ticker_if_any(text, impact):
    text_lower = text.lower()

    if impact == "Stocks":
        for name, ticker in STOCK_TICKERS.items():
            if name in text_lower:
                return ticker
        return "N/A"

    elif impact == "Crypto":
        for name, ticker in CRYPTO_TICKERS.items():
            if name in text_lower:
                return ticker
        return "N/A"

    else:
        return "N/A"

def generate_ascii_report(df):
    columns_for_table = [
        "Title", 
        "Ticker", 
        "Impact",
        "Sentiment",
        "Summary",
        "Link",
        "Published_At",
        "Source"
    ]
    table_data = df[columns_for_table]

    ascii_table = tabulate(table_data, headers="keys", tablefmt="fancy_grid")

    sentiment_counts = df["Sentiment"].value_counts()
    ascii_chart_lines = []
    
    for sentiment_type in ["Bullish", "Bearish", "Neutral"]:
        count = sentiment_counts.get(sentiment_type, 0)
        bar = "-" * count
        ascii_chart_lines.append(f"{sentiment_type:8}: {bar} ({count})")

    ascii_chart = "\n".join(ascii_chart_lines)

    report_str = []
    report_str.append("=== DAILY MARKET REPORT (ASCII) ===\n")
    report_str.append("TABLE OF ARTICLES:\n")
    report_str.append(ascii_table + "\n\n")
    report_str.append("SENTIMENT DISTRIBUTION (ASCII BAR CHART):\n")
    report_str.append(ascii_chart + "\n")

    return "\n".join(report_str)

def generate_report():
    keywords = {
        "crypto": [
            "bitcoin", "btc", "ether", "ethereum", "cryptocurrency", "crypto", 
            "blockchain", "bnb", "ripple", "dogecoin", "doge", "litecoin", "solana"
        ],
        "stocks": [
            "stock", "stocks", "shares", "market", "nasdaq", "dow jones", 
            "s&p", "equities", "bond", "ipo", "wall street",
            "apple", "tesla", "amazon", "microsoft", "google", "nvidia"
        ],
    }

    queries = [
        "stock market",
        "crypto",
        "bitcoin",
        "technology stocks",
        "financial markets",
        "energy sector",
        "healthcare sector",
        "consumer discretionary sector",
        "industrial sector",
        "materials sector",
        "real estate market",
        "utilities sector",
    ]

    combined_articles_data = []

    for q in queries:
        log_colored_message(f"Fetching articles for: {q}", "info")
        articles = get_top_headlines(query=q, page_size=5)
        
        if not articles:
            log_colored_message(f"No articles retrieved for '{q}'.", "warning")
            continue

        for article in articles:
            summary = summarize_article(article)
            full_text = " ".join([
                article.get("title") or "",
                article.get("description") or "",
                article.get("content") or ""
            ])

            sentiment = determine_sentiment(full_text)
            impact = determine_impact(article, keywords)
            ticker = guess_ticker_if_any(full_text, impact)

            combined_articles_data.append({
                "Title": article.get("title", "N/A"),
                "Link": article.get("url", "N/A"),
                "Summary": summary,
                "Impact": impact,               # Stocks, Crypto, or General
                "Sentiment": sentiment,         # Bullish, Bearish, or Neutral
                "Ticker": ticker,               # e.g. AAPL, BTC, etc.
                "Published_At": article.get("publishedAt", "N/A"),
                "Source": article.get("source", {}).get("name", "N/A"),
                "Query": q,                     # which query triggered this
            })
    
    if not combined_articles_data:
        log_colored_message("No articles to report. Exiting.", "error")
        sys.exit(0)

    df = pd.DataFrame(combined_articles_data)

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_folder = f"./reports_{date_str}"
    os.makedirs(output_folder, exist_ok=True)
    log_colored_message(f"Using output folder: {output_folder}", "info")

    csv_file_name = os.path.join(output_folder, f"market_report_{date_str}.csv")
    df.to_csv(csv_file_name, index=False)
    log_colored_message(f"CSV report generated: {csv_file_name}", "success")

    text_file_name = os.path.join(output_folder, f"market_report_{date_str}.txt")
    ascii_report = generate_ascii_report(df)
    with open(text_file_name, "w", encoding="utf-8") as f:
        f.write(ascii_report)
    log_colored_message(f"ASCII text report generated: {text_file_name}", "success")


def display_menu():
    while True:
        print("\n" + Fore.BLUE + "=== Stock & Crypto Market Report Generator ===" + Style.RESET_ALL)
        print("1. Generate today's market report")
        print("2. Exit")
        
        choice = input(Fore.YELLOW + "Enter your choice (1/2): " + Style.RESET_ALL)
        
        if choice == "1":
            generate_report()
        elif choice == "2":
            log_colored_message("Exiting program.", "info")
            sys.exit(0)
        else:
            log_colored_message("Invalid choice. Please try again.", "warning")

if __name__ == "__main__":
    display_menu()

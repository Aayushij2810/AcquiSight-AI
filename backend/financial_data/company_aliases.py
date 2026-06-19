"""
Popular company aliases and legal-name mappings for intelligent resolution.

Covers historical names, brand names, and common shorthand.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompanyEntry:
    ticker: str
    company_name: str
    aliases: tuple[str, ...] = ()


# Curated directory — merged with dynamic Yahoo/NASDAQ search for full coverage.
COMPANY_DIRECTORY: list[CompanyEntry] = [
    CompanyEntry("MSFT", "Microsoft Corporation", ("microsoft", "msft")),
    CompanyEntry("AAPL", "Apple Inc.", ("apple", "aapl")),
    CompanyEntry("GOOGL", "Alphabet Inc.", ("alphabet", "google", "googl", "google inc")),
    CompanyEntry("GOOG", "Alphabet Inc. Class C", ("google class c",)),
    CompanyEntry("META", "Meta Platforms, Inc.", ("meta", "meta platforms", "facebook", "fb")),
    CompanyEntry("AMZN", "Amazon.com, Inc.", ("amazon", "amazon.com", "amzn")),
    CompanyEntry("NVDA", "NVIDIA Corporation", ("nvidia", "nvda", "nvdia")),
    CompanyEntry("TSLA", "Tesla, Inc.", ("tesla", "tsla")),
    CompanyEntry("ADBE", "Adobe Inc.", ("adobe", "adbe")),
    CompanyEntry("CRM", "Salesforce, Inc.", ("salesforce", "crm")),
    CompanyEntry("ORCL", "Oracle Corporation", ("oracle", "orcl")),
    CompanyEntry("NFLX", "Netflix, Inc.", ("netflix", "nflx")),
    CompanyEntry("JPM", "JPMorgan Chase & Co.", ("jpmorgan", "jp morgan", "jpm", "chase")),
    CompanyEntry("V", "Visa Inc.", ("visa",)),
    CompanyEntry("MA", "Mastercard Incorporated", ("mastercard", "ma")),
    CompanyEntry("BABA", "Alibaba Group Holding Limited", ("alibaba", "alibaba group", "baba")),
    CompanyEntry("TTM", "Tata Motors Limited", ("tata motors", "tata", "ttm")),
    CompanyEntry("TCS.NS", "Tata Consultancy Services Limited", ("tcs", "tata consultancy", "tata consultancy services")),
    CompanyEntry("INFY", "Infosys Limited", ("infosys", "infy")),
    CompanyEntry("WIT", "Wipro Limited", ("wipro", "wit")),
    CompanyEntry("RELIANCE.NS", "Reliance Industries Limited", ("reliance", "reliance industries")),
    CompanyEntry("005930.KS", "Samsung Electronics Co., Ltd.", ("samsung",)),
    CompanyEntry("TM", "Toyota Motor Corporation", ("toyota", "tm")),
    CompanyEntry("NSRGY", "Nestlé S.A.", ("nestle", "nestlé", "nsrgy")),
    CompanyEntry("BRK.B", "Berkshire Hathaway Inc.", ("berkshire", "berkshire hathaway", "brk.b", "brk-b")),
    CompanyEntry("HSBC", "HSBC Holdings plc", ("hsbc",)),
    CompanyEntry("SHEL", "Shell plc", ("shell", "shel")),
    CompanyEntry("UL", "Unilever PLC", ("unilever", "ul")),
    CompanyEntry("ASML", "ASML Holding N.V.", ("asml",)),
    CompanyEntry("TSM", "Taiwan Semiconductor Manufacturing Company Limited", ("tsmc", "taiwan semiconductor", "tsm")),
    CompanyEntry("BYDDY", "BYD Company Limited", ("byd", "byddy")),
    CompanyEntry("WMT", "Walmart Inc.", ("walmart", "wmt")),
    CompanyEntry("COST", "Costco Wholesale Corporation", ("costco", "cost")),
    CompanyEntry("DIS", "The Walt Disney Company", ("disney", "dis")),
    CompanyEntry("XYZ", "Block, Inc.", ("block", "square", "xyz")),
    CompanyEntry("INTC", "Intel Corporation", ("intel", "intc")),
    CompanyEntry("AMD", "Advanced Micro Devices, Inc.", ("amd",)),
    CompanyEntry("IBM", "International Business Machines Corporation", ("ibm",)),
    CompanyEntry("CSCO", "Cisco Systems, Inc.", ("cisco", "csco")),
    CompanyEntry("PYPL", "PayPal Holdings, Inc.", ("paypal", "pypl")),
    CompanyEntry("UBER", "Uber Technologies, Inc.", ("uber",)),
    CompanyEntry("ABNB", "Airbnb, Inc.", ("airbnb", "abnb")),
    CompanyEntry("SNOW", "Snowflake Inc.", ("snowflake", "snow")),
    CompanyEntry("PLTR", "Palantir Technologies Inc.", ("palantir", "pltr")),
    CompanyEntry("COIN", "Coinbase Global, Inc.", ("coinbase", "coin")),
    CompanyEntry("SHOP", "Shopify Inc.", ("shopify", "shop")),
    CompanyEntry("MSTR", "MicroStrategy Incorporated", ("microstrategy", "mstr")),
    CompanyEntry("MU", "Micron Technology, Inc.", ("micron", "mu")),
]

# Historical / rebranding aliases (Step 4).
HISTORICAL_ALIASES: dict[str, str] = {
    "google": "GOOGL",
    "google inc": "GOOGL",
    "facebook": "META",
    "fb": "META",
    "square": "XYZ",
    "square inc": "XYZ",
    "adobe systems": "ADBE",
    "nvidia corp": "NVDA",
    "amazon.com": "AMZN",
}

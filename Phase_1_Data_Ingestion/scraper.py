import requests
from bs4 import BeautifulSoup
import json
import os
import re

CORPUS_URLS = {
    "HDFC Flexi Cap Fund": [
        "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth"
    ],
    "HDFC ELSS Tax Saver": [
        "https://groww.in/mutual-funds/hdfc-taxsaver-direct-growth"
    ],
    "HDFC Mid-Cap Opportunities Fund": [
        "https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth"
    ],
    "HDFC Liquid Fund": [
        "https://groww.in/mutual-funds/hdfc-liquid-fund-direct-growth"
    ],
    "HDFC Small Cap Fund": [
        "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth"
    ],
    "Official Guidelines & Education": [
        "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=3&ssid=13&smid=0",
        "https://www.amfiindia.com/investor-corner/knowledge-center/what-are-mutual-funds.jsp"
    ]
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

def clean_text(text):
    """Clean extra whitespaces and newlines from text."""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_from_url(url):
    """Fetches a URL and extracts readable text. For Groww, extracts exact JSON metrics."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # If it's a groww.in scheme page, extract the pristine JSON metrics!
        if 'groww.in/mutual-funds/' in url:
            script = soup.find('script', id='__NEXT_DATA__')
            if script:
                data = json.loads(script.string)
                mfs = data.get('props', {}).get('pageProps', {}).get('mfServerSideData', {})
                if mfs:
                    # Construct a perfect text block, impervious to HTML table scrambling
                    fact_sheet = (
                        f"FACT SHEET FOR {mfs.get('scheme_name')}:\n"
                        f"Category: {mfs.get('sub_category')}\n"
                        f"NAV: ₹{mfs.get('nav')} (as on {mfs.get('nav_date')})\n"
                        f"AUM (Fund Size): ₹{mfs.get('aum')} Cr\n"
                        f"Expense Ratio: {mfs.get('expense_ratio')}%\n"
                        f"Exit Load: {mfs.get('exit_load')}\n"
                        f"Minimum SIP: ₹{mfs.get('sip_minimum_installment_amount')}\n"
                        f"Fund House: HDFC\n"
                        f"Risk Rating: {mfs.get('risk_rating', 'Very High')}\n"
                    )
                    # We still extract the rest of the text for general context (holdings, etc)
                    for s in soup(["script", "style", "nav", "footer", "header"]):
                        s.extract()
                    general_text = clean_text(soup.get_text(separator=' '))
                    return fact_sheet + "\n\n" + general_text
        
        # Default text extraction for AMFI/SEBI
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
        text = soup.get_text(separator=' ')
        return clean_text(text)
        
    except Exception as e:
        print(f"Error extracting {url}: {e}")
        return None

def ingest_data(output_file):
    """Main pipeline to run extraction across all targeted URLs."""
    ingested_data = []
    
    print("Starting Phase 1 Ingestion...")
    for scheme, urls in CORPUS_URLS.items():
        print(f"Processing Category: {scheme}")
        for url in urls:
            print(f"  -> Scraping: {url}")
            content = extract_text_from_url(url)
            
            if content and len(content) > 100:
                # We save the metadata needed for citation later
                record = {
                    "scheme_name": scheme,
                    "source_url": url,
                    "content": content
                }
                ingested_data.append(record)
                print(f"     [SUCCESS] Extracted {len(content)} characters.")
            else:
                print(f"     [FAILED] Could not extract meaningful content.")
                
    # Hardcoding the fundamental educational definition
    educational_fact = {
        "scheme_name": "Mutual Fund Education",
        "source_url": "https://www.amfiindia.com/",
        "content": "A mutual fund is a financial vehicle that pools money from multiple investors to purchase a diversified portfolio of securities like stocks, bonds, or money market instruments. They are managed by professional fund managers who allocate the fund's assets to produce capital gains or income for the investors. Mutual funds give small or individual investors access to professionally managed portfolios of equities, bonds, and other securities. The price of a mutual fund is known as its Net Asset Value (NAV)."
    }
    ingested_data.append(educational_fact)
    print("     [SUCCESS] Appended Educational Definitions.")
        
    # Save to JSON for Phase 2
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ingested_data, f, indent=4, ensure_ascii=False)
        
    print(f"\nIngestion Complete. Saved {len(ingested_data)} records to {output_file}.")
    return ingested_data

if __name__ == "__main__":
    # Ensure current directory for output
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, "extracted_corpus.json")
    ingest_data(output_path)

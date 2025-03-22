#!/usr/bin/env python3
"""
RLG Backlink Checker with Advanced Enhancements
------------------------------------------------
This script ethically checks for backlinks to a target domain by processing candidate URLs.
It features:
  • Robots.txt compliance checking.
  • Concurrent URL processing with progress reporting.
  • Advanced region detection using tldextract.
  • Placeholder integration for external SEO metrics (e.g., PageSpeed Insights).
  • Detailed logging and robust error handling.
  • Automated CSV reporting with backlink details and region information.
  • Placeholders for sending email alerts and integrating with the RLG Super Tool API.

Ethical Considerations:
  • Only accesses publicly available pages.
  • Respects robots.txt directives.
  • Intended for backlink analysis on domains you own or have permission to check.
"""

import os
import csv
import re
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
from tqdm import tqdm
from datetime import datetime
import tldextract

# ------------------------- Configuration -------------------------

TARGET_DOMAIN = "example.com"         # Replace with your target domain (without protocol)
INPUT_CSV = "candidate_urls.csv"        # CSV file with a column "url" listing candidate page URLs
OUTPUT_CSV = "backlinks_report.csv"     # Output CSV filename
REQUEST_TIMEOUT = 10                    # seconds timeout for HTTP requests
MAX_WORKERS = 10                        # Number of concurrent workers
USER_AGENT = "Mozilla/5.0 (compatible; RLGBacklinkChecker/1.0; +http://www.yourdomain.com/bot)"

# Email Alert Configuration (placeholder)
EMAIL_ALERTS_ENABLED = False            # Set to True to enable email alerts
EMAIL_RECIPIENTS = ["admin@rlgdata.com"]
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@example.com"
SMTP_PASSWORD = "your-email-password"

# RLG Super Tool API Integration (placeholder)
SUPER_TOOL_API_URL = "https://api.rlgsupertool.com/backlinks"
SUPER_TOOL_API_KEY = "your-super-tool-api-key"

# ------------------------- Logging Setup -------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("backlinks.log"), logging.StreamHandler()]
)

# ------------------------- Helper Functions -------------------------

def is_allowed_by_robots(url):
    """
    Check if the URL is allowed to be fetched according to robots.txt.
    """
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    robots_url = urljoin(base_url, "/robots.txt")
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        allowed = rp.can_fetch(USER_AGENT, url)
        if not allowed:
            logging.info(f"Disallowed by robots.txt: {url}")
        return allowed
    except Exception as e:
        logging.warning(f"Robots.txt check failed for {url}: {e}")
        return True  # If unable to read robots.txt, assume allowed ethically

def fetch_page(url):
    """
    Fetch the page content from the URL with proper timeout and headers.
    Returns (url, status_code, content) tuple.
    """
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
        return url, response.status_code, response.text
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return url, None, None

def extract_backlinks(url, html):
    """
    Extract all anchor tags whose href contains TARGET_DOMAIN.
    Returns a list of dictionaries with details.
    """
    backlinks = []
    if not html:
        return backlinks
    try:
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("title")
        page_title = title_tag.get_text().strip() if title_tag else "N/A"
        anchors = soup.find_all("a", href=True)
        for anchor in anchors:
            href = anchor["href"].strip()
            anchor_text = anchor.get_text().strip()
            # Resolve relative URLs
            href_full = urljoin(url, href)
            if TARGET_DOMAIN.lower() in href_full.lower():
                region = guess_region(href_full)
                seo_metrics = get_seo_metrics(href_full)  # Placeholder for SEO metrics integration
                backlinks.append({
                    "page_url": url,
                    "page_title": page_title,
                    "anchor_text": anchor_text,
                    "backlink_url": href_full,
                    "region": region,
                    "seo_metrics": seo_metrics
                })
    except Exception as e:
        logging.error(f"Error parsing HTML for {url}: {e}")
    return backlinks

def guess_region(url):
    """
    Uses tldextract to extract domain parts and guess region from TLD.
    This function can be extended with a more robust region detection logic.
    """
    ext = tldextract.extract(url)
    tld = ext.suffix.lower()
    region_map = {
        "uk": "United Kingdom",
        "ca": "Canada",
        "au": "Australia",
        "de": "Germany",
        "fr": "France",
        # Add more mappings as needed
    }
    return region_map.get(tld, "Global")

def get_seo_metrics(url):
    """
    Placeholder function to fetch SEO metrics for a given URL.
    You could integrate with external APIs (e.g., Google PageSpeed Insights, Moz, Ahrefs).
    For now, it returns a dummy dictionary.
    """
    # For demonstration purposes, return dummy SEO metrics.
    return {
        "page_speed": "85",  # Example: PageSpeed score out of 100
        "domain_authority": "50"  # Example: Domain authority score
    }

def process_url(url):
    """
    Processes a single URL: check robots.txt, fetch the page, and extract backlinks.
    Returns a list of backlink details.
    """
    if not is_allowed_by_robots(url):
        return []
    url, status, content = fetch_page(url)
    if status and status == 200:
        return extract_backlinks(url, content)
    else:
        logging.warning(f"Failed to fetch {url} with status: {status}")
        return []

def load_candidate_urls(input_csv):
    """
    Loads candidate URLs from the specified CSV file.
    Expects a column named "url".
    """
    try:
        df = pd.read_csv(input_csv)
        urls = df["url"].dropna().tolist()
        logging.info(f"Loaded {len(urls)} candidate URLs.")
        return urls
    except Exception as e:
        logging.error(f"Error loading candidate URLs: {e}")
        return []

def send_email_alert(message):
    """
    Placeholder for sending email alerts using smtplib.
    Replace with your implementation if email alerts are required.
    """
    if not EMAIL_ALERTS_ENABLED:
        logging.info("Email alerts are disabled.")
        return
    # (Insert smtplib email sending code here)
    logging.info(f"Email alert sent: {message}")

def send_to_super_tool(report):
    """
    Placeholder function for sending the report to the RLG Super Tool API.
    """
    try:
        headers = {"Authorization": f"Bearer {SUPER_TOOL_API_KEY}", "Content-Type": "application/json"}
        response = requests.post(SUPER_TOOL_API_URL, json=report, headers=headers)
        if response.status_code == 200:
            logging.info("Successfully sent report to RLG Super Tool.")
        else:
            logging.error(f"Failed to send report to RLG Super Tool: {response.status_code} {response.text}")
    except Exception as e:
        logging.error(f"Error sending report to RLG Super Tool: {e}")

def save_report(backlinks_list, output_csv):
    """
    Saves the backlinks report to a CSV file.
    """
    if not backlinks_list:
        logging.info("No backlinks found.")
        return
    try:
        df = pd.DataFrame(backlinks_list)
        df.to_csv(output_csv, index=False)
        logging.info(f"Backlinks report saved to {output_csv}")
    except Exception as e:
        logging.error(f"Error saving report: {e}")

# ------------------------- Main Processing -------------------------

def main():
    candidate_urls = load_candidate_urls(INPUT_CSV)
    if not candidate_urls:
        logging.error("No candidate URLs to process.")
        return

    all_backlinks = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(process_url, url): url for url in candidate_urls}
        for future in tqdm(as_completed(future_to_url), total=len(candidate_urls), desc="Processing URLs"):
            url = future_to_url[future]
            try:
                backlinks = future.result()
                all_backlinks.extend(backlinks)
            except Exception as exc:
                logging.error(f"Exception for {url}: {exc}")

    # Save the final report
    save_report(all_backlinks, OUTPUT_CSV)
    
    # Send the report to the RLG Super Tool (placeholder integration)
    if all_backlinks:
        report = {"timestamp": datetime.now().isoformat(), "backlinks": all_backlinks}
        send_to_super_tool(report)
    
    # If any suspicious backlinks (e.g., region not in a safe list), send email alert
    safe_regions = {"Global", "United Kingdom", "Germany", "France", "Canada", "Australia"}
    suspicious_backlinks = [b for b in all_backlinks if b["region"] not in safe_regions]
    if suspicious_backlinks:
        send_email_alert(f"Suspicious backlinks detected: {len(suspicious_backlinks)} items.")

if __name__ == "__main__":
    main()

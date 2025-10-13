import os
import time
import requests
import xml.etree.ElementTree as ET

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from project import models

BASE_URL = "http://export.arxiv.org/api/query"
DOMAIN = "cs"
SUBDOMAIN = "DB"
MAX_RESULTS = 50
BATCH_SIZE = 25
SLEEP_INTERVAL = 4 

NAMESPACE = {
    'atom': 'http://www.w3.org/2005/Atom',
    'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'
}

def fetch_arxiv_batch(start: int, batch_size: int):
    params = {
        "search_query": f"cat:{DOMAIN}.{SUBDOMAIN}",
        "start": start,
        "max_results": batch_size
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            headers={"Accept": "application/xml"},
        )
        print(response.status_code)
        print(response.text)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch data: {e}")
        return None

def parse_entries(xml_data: str):
    root = ET.fromstring(xml_data)
    entries = root.findall('atom:entry', NAMESPACE)
    parsed = []

    for entry in entries:
        data = {
            'paper_id': entry.find('atom:id', NAMESPACE).text if entry.find('atom:id', NAMESPACE) else None,
            'title': entry.find('atom:title', NAMESPACE).text if entry.find('atom:title', NAMESPACE) else None,
            'published': entry.find('atom:published', NAMESPACE).text if entry.find('atom:published', NAMESPACE) else None,
            'author': entry.find('atom:author/atom:name', NAMESPACE).text if entry.find('atom:author/atom:name', NAMESPACE) else None,
            'summary': entry.find('atom:summary', NAMESPACE).text if entry.find('atom:summary', NAMESPACE) else None,
            'domain': DOMAIN,
            'subdomain': SUBDOMAIN,
            'pdf_link': None,
            'reference_link': None
        }

        for link in entry.findall('atom:link', NAMESPACE):
            href = link.attrib.get('href')
            title_attr = link.attrib.get('title', '')
            type_attr = link.attrib.get('type', '')
            if title_attr and 'pdf' in title_attr.lower():
                data['pdf_link'] = href
            if type_attr == 'text/html' and 'arxiv.org' in href:
                data['reference_link'] = href

        parsed.append(data)

    return parsed

def main():
    start = 0
    all_entries = []

    while start < MAX_RESULTS:
        xml_data = fetch_arxiv_batch(start, min(BATCH_SIZE, MAX_RESULTS - start))
        if not xml_data:
            break

        root = ET.fromstring(xml_data)
        total_results_elem = root.find('opensearch:totalResults', NAMESPACE)
        total_results = int(total_results_elem.text) if total_results_elem is not None else 0

        if total_results == 0:
            print("[INFO] No papers found for this category.")
            break

        entries = parse_entries(xml_data)
        if not entries:
            print("[INFO] No more entries found.")
            break

        all_entries.extend(entries)
        start += BATCH_SIZE
        print(f"[INFO] Fetched {len(all_entries)} papers so far...")
        time.sleep(SLEEP_INTERVAL)

    if all_entries:
        print(f"[INFO] Inserting {len(all_entries)} papers into database...")
        models.InsertFiles(all_entries)
    else:
        print("[INFO] No papers to insert.")

if __name__ == "__main__":
    main()
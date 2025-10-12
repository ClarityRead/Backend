#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import requests 
import xml.etree.ElementTree as ET
import json

base_url = "http://export.arxiv.org/api/query"

params = {
    "search_query": "cat:cs.AI",  # For example, search in the Computer Science > Artificial Intelligence category
    "start": 0,                   # Starting index for results
    "max_results": 10,             # Maximum number of results to return
    "format": "json"              # Specify that you want the output in JSON format
}

headers = {"Accept": "application/xml"}

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

    from project import models

    response = requests.get(base_url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.text
        root = ET.fromstring(data)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', namespace)
        entries_data = []

        for entry in entries:
            entry_data = {
                'paper_id': entry.find('atom:id', namespace).text if entry.find('atom:id', namespace) is not None else None,
                'title': entry.find('atom:title', namespace).text if entry.find('atom:title', namespace) is not None else None,
                'published': entry.find('atom:published', namespace).text if entry.find('atom:published', namespace) is not None else None,
                'author': entry.find('atom:author/atom:name', namespace).text if entry.find('atom:author/atom:name', namespace) is not None else None,
                'summary': entry.find('atom:summary', namespace).text if entry.find('atom:summary', namespace) is not None else None,
                'domain': 'cs',
                'subdomain': 'ai'
            }

            pdf_link = None
            reference_link = None

            for link in entry.findall('atom:link', namespace):
                if link.attrib.get('title') and 'pdf' in link.attrib['title'].lower():
                    pdf_link = link.attrib.get('href')
                if link.attrib.get('type') == 'text/html' and 'arxiv.org' in link.attrib.get('href'):
                    reference_link = link.attrib.get('href')

            entry_data["pdf_link"] = pdf_link
            entry_data["reference_link"] = reference_link
            entries_data.append(entry_data)

        models.InsertFiles(entries_data)

    else:
        print(f"Error: {response.status_code}")
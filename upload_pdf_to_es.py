import os
import sys
import json
import re
import requests
from pdfminer.high_level import extract_text

# Elasticsearch Configuration
ES_HOST = "http://localhost:9200"
INDEX_NAME = "lines"

# PDF file path from command line arguments
if len(sys.argv) != 2:
    print("Usage: python upload_pdf_to_es.py <path_to_pdf>")
    sys.exit(1)
PDF_FILE = sys.argv[1]

# Define the index mapping and settings
INDEX_CONFIG = {
    "settings": {
        "analysis": {
            "analyzer": {
                "muskogean_preserve": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase"
                    ]
                },
                "muskogean_normalized": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "asciifolding"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "filename": {
                "type": "keyword"
            },
            "line_number": {
                "type": "integer"
            },
            "content": {
                "type": "text",
                "fields": {
                    "preserve": {
                        "type": "text",
                        "analyzer": "muskogean_preserve"
                    },
                    "normalized": {
                        "type": "text",
                        "analyzer": "muskogean_normalized"
                    }
                }
            }
            # You can add additional metadata fields here (e.g., publication_date, source)
        }
    }
}

# Create the index if it does not exist
def create_index():
    url = f"{ES_HOST}/{INDEX_NAME}"
    # Check if the index already exists
    response = requests.head(url)
    if response.status_code == 200:
        print(f"Index '{INDEX_NAME}' already exists.")
        return
    # Create the index
    response = requests.put(url, headers={"Content-Type": "application/json"}, data=json.dumps(INDEX_CONFIG))
    if response.status_code in [200, 201]:
        print(f"Index '{INDEX_NAME}' created successfully.")
    else:
        print(f"Error creating index: {response.text}")
        sys.exit(1)

# Extract text from PDF and split into lines
def extract_lines_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    lines = text.split("\n")  # Split into lines
    lines = process_lines(lines)  # Process lines to replace special characters
    return [line for line in lines if line and "·" not in line]  # Remove empty lines & lines with `·`

# Process lines to replace PDF artifacts with proper characters
def process_lines(lines):
    replacements = {
        "a": "ą̄",
        "ē": "ę̄",
        "i": "į̄",
        "o": "ǫ",
        "u": "ų",
        "v": "v̨"
    }
    def replace_cid3(match):
        letter = match.group(1)
        return replacements.get(letter, letter)
    return [
        re.sub(r"([aeiouvēv])\(cid:3\)", replace_cid3, line).replace("∑", "ē").strip()
        for line in lines if line.strip() and "·" not in line
    ]

# Send each line as a separate document in Elasticsearch
def send_lines_to_elasticsearch(filename, lines):
    for idx, line in enumerate(lines):
        doc = {
            "filename": filename,
            "line_number": idx + 1,
            "content": line
        }
        url = f"{ES_HOST}/{INDEX_NAME}/_doc/{filename}-{idx+1}"
        headers = {"Content-Type": "application/json"}
        response = requests.put(url, headers=headers, data=json.dumps(doc))
        if response.status_code in [200, 201]:
            print(f"Indexed line {idx+1} from {filename}")
        else:
            print(f"Error indexing line {idx+1}: {response.text}")

# Main execution
if __name__ == "__main__":
    create_index()
    lines = extract_lines_from_pdf(PDF_FILE)
    send_lines_to_elasticsearch(os.path.basename(PDF_FILE), lines)


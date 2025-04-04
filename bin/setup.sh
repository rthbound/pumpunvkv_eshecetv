#!/bin/sh

python3 -m venv pumpunvkv_eshecetv
source pumpunvkv_eshecetv/bin/activate
pip install pdfminer.six requests

# If user has docker installed, build the docker image
# otherwise instruct user to install docker and quit early
if ! command -v docker &> /dev/null
then
    echo "Docker could not be found. Please install Docker to use this script."
    exit
fi

docker-compose build

echo "\n"
echo "Python dependencies installed in the virtual environment 'pumpunvkv_eshecetv'."
echo "To activate the virtual environment, run:"
echo "\n\tsource pumpunvkv_eshecetv/bin/activate"

echo "To start the Elasticsearch container, run:"
echo "\n\tdocker-compose up -d"

echo "\nThen start indexing PDFs with the command:"
echo "\n\tpython upload_pdf_to_es.py haas_hill.pdf"

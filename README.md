# Installation / Setup
Run `bin/setup.sh` and follow instructions to finish setup.

# Indexing
The setup script outputs these instructions, but here they are
again:

1. Run `docker-compose up -d` to start the docker containers.
2. Run `source pumpunvkv_eshecetv/bin/activate` to activate the virtual environment where
   the Python script's dependencies are installed.
3. Run `python upload_pdf_to_es.py cen_nak_cokv.pdf` to upload a PDF file to Elasticsearch.

# PDFs
Out of respect for copyrights, we do not include any of the
PDFs you might wish to index within this repo itself.

Some texts to index:

- Haas/Hill texts
- Totkv Mocvse E-book
- William & Mary interview series transcripts
- Pum Mvhayv Toyetskat (letters to Ann Eliza Worcester)

Some PDFs we have available need their OCR derived data cleaned up.

e.g. See: https://github.com/rthbound/CENESES_KIHOCAT

# Searching

Kibana is provided in the docker-compose.yml file. After starting the
environment, and after indexing documents, visit http://localhost:5601/app/kibana#/dev_tools/console

From there you can issue queries, for example:

```
GET _search
{
  "size": 1000,
  "query": {
    "regexp": {
      "content.normalized": "cetak.*"
    }
  },
  "highlight": {
    "pre_tags": ["<i>"],
    "post_tags": ["</i>"],
    "fields": {
      "content.normalized": {}
    }
  }
}
```

or

```
GET _search
{
  "query": {
    "regexp": {
      "content.normalized": ".*(hoyvk|vkhoy|akhoy|hoyak|hoyepvk|vkephoy|akephoy|hoyepak).*"
    }
  }
}
```

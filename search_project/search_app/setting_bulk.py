# search_app/setting_bulk.py

from elasticsearch import Elasticsearch
import json
es = Elasticsearch(hosts='localhost', port=9200)
if es.indices.exists(index='dictionary'):
    pass
else:
    es.indices.create(
        index='dictionary',
        body={
            "settings": {
                "index": {
                    "analysis": {
                        "analyzer": {
                            "my_analyzer": {
                                "type": "custom",
                                "tokenizer": "nori_tokenizer"
                            }
                        }
                    }
                }
            },
            "mappings": {
                    "properties": {
                        "id": {
                            "type": "long"
                        },
                        "title": {
                            "type": "text",
                            "analyzer": "my_analyzer"
                        },
                        "keyword": {
                            "type": "text",
                            "analyzer": "my_analyzer"
                        },
                        "field": {
                            "type": "text",
                            "analyzer": "my_analyzer"
                        },
                        "type": {
                            "type": "text",
                            "analyzer": "my_analyzer"
                        },
                    }
            }
        }
    )


with open("dictionary_data.json", encoding='utf-8') as json_file:
    json_data = json.loads(json_file.read())

body = ""
for i in json_data:
    body = body + json.dumps({"index": {"_index": "dictionary"}}) + '\n'
    body = body + json.dumps(i, ensure_ascii=False) + '\n'

es.bulk(body)
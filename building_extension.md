## Extension Development
This plugin only ships with simple indexer, when the JSON file increases in size, you may want to use a search engine like elasticsearch. 

If you want to create your own indexer, this guide to extension development will help you build your first extension and get it running. 

## Anatomy of an Extension
We recommend the directory structure below.

```
├── MANIFEST.in
├── ascii_binder_search
│   ├── __init__.py
│   ├── indexers
│   │   ├── __init__.py
│   │   └── something.py
│   └── static
│       └── something
│           └── search.js
├── readme.md
└── setup.py
```

Here "something" is the name of your extension

## “Hello extension!”
For the purposes of this example, we will create a basic extension that indexes and queries the data into elastic search.

First we create the following folder structure:
```
├── MANIFEST.in
├── ascii_binder_search
│   ├── __init__.py
│   ├── indexers
│   │   ├── __init__.py
│   │   └── elastic_search.py
│   └── static
│       └── elastic_search
│           └── search.js
├── readme.md
└── setup.py
```

## setup.py
The next file that is absolutely required is ``` setup.py ``` file which is used to install your extension. The following contents are something you can work with:

Please make sure you don't change the namespace since when base indexer searches for the modules in the same name space.

``` python
from setuptools import setup


setup(
    name="ascii_binder_search_elastic_search",
    version="0.0.1",
    author="YOUR NAME",
    author_email="your-email@example.com",
    description=("Very short description"),
    packages=[
                'ascii_binder_search',
                'ascii_binder_search.indexers',
            ],
    license="BSD",
    keywords="Asciibinder, ascii_binder_search, ascii_binder_search_elastic_search",
    url="https://github.com/smitthakkar96/ascii_binder_search_plugin",
    install_requires=['elasticsearch'],
    include_package_data=True,
    zip_safe=False,
    namespaces=[
        'ascii_binder_search.indexers'
    ],

)

```

## MANIFEST.in

Add the paths of static assets that you want to include with your extension in MANIFEST.in

That’s a lot of code but you can really just copy/paste 
that from existing extensions and adapt.

## elastic_search.py
Now this is where your python code for the extension goes.

``` 
import argparse
import json
import pkg_resources
import os

from ascii_binder_search.indexer import Indexer
from elasticsearch import Elasticsearch, helpers

class ElasticSearch(Indexer):
    """ Elastic Search implementation for indexer """

    def index(self, dump, distro, site_folder):
        """
        Override this method to index the data to your 
        preferred search engine.
        args:
            dump - dictionary of data that is to be indexed
            it would have topic_url, title, content, site_name
            distro - string containing the distro
            site_folder - name of the folder containing the static html files
            code to index data to elastic search
        """
        pass
    
    def parse_indexer_arguments(self):
        """ Overriding this method is 
        needed when you want to parse indexer 
        specific arguments.
        
        It must set self.backend_args with the parsed args object
        
        """
        pass
        
```

Above are the two methods that you will want to override most of the time. Below is actual elastic_search.py from the extension repo.

``` python
import argparse
import json
import pkg_resources
import os

from ascii_binder_search.indexer import Indexer
from elasticsearch import Elasticsearch, helpers


class ElasticSearch(Indexer):
    """ Elastic Search implementation for indexer """

    def index(self, dump, distro, site_folder):
        # prepare data for bulk index
        data = []
        for version in dump:
            for d in dump[version]:
                d['version'] = version
                d['distro'] = distro
                data.append({
                    "_index": self.backend_args.index_name,
                    "_type": "doc_content",
                    "_source": d
                })
        helpers.bulk(self.es, data)
        print("Data Indexed successfully")
        meta_data_file = open('_package/{}/meta_data.json'.format(site_folder), 'w+')
        meta_data = {
            "distro": distro,
            "versions": list(dump.keys()),
            "es_url": self.backend_args.elastic_search_url,
            "index_name": self.backend_args.index_name
        }
        json.dump(meta_data, meta_data_file)
        meta_data_file.close()

    def parse_indexer_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-e', '--elastic-search-url', required=True)
        parser.add_argument('-i', '--index-name', default='ASCII_BINDER_DOCS_INDEX')
        args, action = parser.parse_known_args()
        self.backend_args = args
        self.prepare_index()

    def prepare_index(self):
        dist = pkg_resources.get_distribution('ascii_binder_search_elastic_search')
        self.es = Elasticsearch(hosts=[self.backend_args.elastic_search_url])
        if self.es.indices.exists(self.backend_args.index_name):
            print("deleting '%s' index..." % (self.backend_args.index_name))
            res = self.es.indices.delete(index=self.backend_args.index_name)
            print(" response: '%s'" % (res))
            print("creating '%s' index..." % (self.backend_args.index_name))
            res = self.es.indices.create(index=self.backend_args.index_name)
            print(" response: '%s'" % (res))
```

## search.js
search.js is responsible for fetching data on client size, display it and paginate it.

``` js
function preInit() {}
function onSearch(searchText) {
    return  new Promise(function(resolve, reject) {});
}
```

``` preinit ``` method is called to fetch metadata like distro_name, es_url, index_name.

``` onSearch ``` method is called fetch data from search engine or file system, paginate and display it.

Below is the actual search.js from the plugin repo

``` js
var distro_name;
var distro_name;
var es_url;
var index_name;

function preInit() {
    indexes = {};
    axios.get('meta_data.json')
        .then(function(response) {
            let versions = response.data['versions'];
            distro_name = response.data['distro'];
            es_url = response.data['es_url'];
            index_name = response.data['index_name'];
            let url = new URL(window.location.href);
            let searchText = url.searchParams.get('search-term');
            let version = url.searchParams.get('version');
            console.log(versions);
            let selectOptions = [];
            for (let i = 0; i < versions.length; i++) {
                console.log('data_' + versions[i]);
                selectOptions.push(`<option value="${versions[i]}">${versions[i]}</option>`);
            }
            $('select').html(selectOptions);
            if (version) {
                $('select').val(version);
            }
        })
        .catch(function(error) {
            console.log(error);
            alert("Something went wrong!");
        });
}


let onSearch = function(searchText) {
    return new Promise(function(resolve, reject) {
        let url = `http://${es_url}/${index_name}/doc_content/_search?size=10000`;
        let query = {
            "query": {
                "bool": {
                    "must": [{
                            "match": {
                                "distro": distro_name
                            }
                        },
                        {
                            "match": {
                                "version": $('select').val()
                            }
                        }
                    ],
                    "should": [{
                            "match": {
                                "title": searchText
                            }
                        },
                        {
                            "match": {
                                "content": searchText
                            }
                        }
                    ]
                }
            }
        }
        this.axios.post(url, query).then(function(response) {
            let results = response.data.hits.hits.map(function(value) { return { doc: value._source }; })
            resolve(results);
        });
    });
}

initPlugin(preInit, onSearch);
```

If you are stuck while building the extension feel free to contact me or nigel.

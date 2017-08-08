""" This is a small plugin that can be used to implement search in your asciibinder project. """

import os
import sys
import argparse
from collections import defaultdict
import importlib

import yaml
from bs4 import BeautifulSoup
import codecs
import pkg_resources
import pkgutil

from ascii_binder_search.lib import is_packaged, repo_check, distro_exists, find_and_parse_sitemap
from ascii_binder_search.lib import copy_static_assets
import ascii_binder_search.indexers

dist = pkg_resources.get_distribution('ascii_binder_search')

static_dir = os.path.join(dist.location, 'ascii_binder_search/static')

verbose = False


class Indexer(object):
    """ Abstract class for indexer """

    def __init__(self, verbose, static_dir):
        self.verbose = verbose
        self.static_dir = static_dir
        self.backend_static_dir = None

    def parse_html(self, doc_path):
        """ Parses the title and the main article content from the documentation file
        and returns it as dict
        Override this method if needed.
        """
        try:
            doc_file = codecs.open(doc_path, 'r')
            soup = BeautifulSoup(doc_file.read(), "lxml")
            title = soup.find('title').get_text()
            ptags = soup.findAll('div', class_="paragraph")
            content = ''
            for p in ptags:
                content += p.get_text()
            return {"title": title, "content": content}
        except IndexError:
            return {"title": "", "content": ""}

    def run(self):
        """ Executes the indexer """
        self.parse_indexer_arguments()
        with open('_distro_map.yml') as distro_map_yml:
            distro_map = yaml.load(distro_map_yml)
            for distro in distro_map:
                site_folder = distro_map[distro]['site']
                data = defaultdict(list)
                if not distro_exists(site_folder):
                    continue
                sitemap = find_and_parse_sitemap(site_folder)
                urls = sitemap['urlset']['url']
                site_name = urls[0]['loc']
                for url in urls:
                    # If the url is equal to site_name or url has index.html
                    # Then ignore it since they won't have any documentation
                    if site_name == url['loc'] or 'index.html' in url['loc']:
                        continue
                    # HACK
                    # Things act differently if the site url does not end with /
                    # so appending / it if not present
                    if site_name[-1] != '/':
                        site_name += '/'
                    topic_path = url['loc'].replace(site_name, "")
                    doc_content = self.parse_html('_package' + '/' + site_folder + '/' + topic_path)
                    version = topic_path[:topic_path.index('/')]
                    if doc_content:
                        data[version].append({
                            "topic_url": topic_path,
                            "title": doc_content['title'],
                            "content": doc_content['content'],
                            "site_name": site_name
                        })
                copy_static_assets('_package/{}/'.format(site_folder),
                                   self.static_dir, self.verbose)
                if self.backend_static_dir:
                    copy_static_assets('_package/{}/'.format(site_folder),
                                       os.path.join(self.static_dir, self.backend_static_dir),
                                       self.verbose)
                self.index(data, distro, site_folder)

    def index(self, dump, distro, site_folder):
        """ This method is called after successful parsing of content.
        dump will have the following keys, the data dump will be grouped by
        version. It is called after every successive parsing of docs of a distro.
            - topic_url
            - title
            - content
            - site_name
        """
        raise NotImplementedError("You must override index")

    def parse_indexer_arguments(self):
        """ Add parser to parse backend specific arguments
        override this method if needed
        Return the dict of args or else the code will break
        """
        return {}


def find_indexers(top_package):
    candidates = pkgutil.walk_packages(top_package.__path__, prefix=top_package.__name__ + '.')
    modules = [name for _, name, is_pkg in candidates if not is_pkg]
    return _import_indexers(modules)


def _import_indexers(modules):
    for module in modules:
        importlib.import_module(module)
    bkls = _filter_classes(Indexer.__subclasses__(), modules)
    backends = {name: kls for name, kls in bkls}
    return backends


def _filter_classes(klasses, modules):
    for kls in klasses:
        m = kls.__module__

        if m not in modules:
            continue

        name = m.split('.')[-1]

        yield name, kls


def main():
    global verbose, static_dir
    if not repo_check():
        sys.exit(1)
    if not is_packaged():
        answer = input("Site must be packaged before generating docs."
                       "Would you like to package it? [Y/N] ")
        if answer in ['Y', 'y', 'yes']:
            os.system('asciibinder package')
        else:
            sys.exit()

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--static-dir', default=static_dir)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-i', '--indexer', required=True)

    args, options = parser.parse_known_args()
    if args.static_dir:
        static_dir = args.static_dir

    if args.verbose:
        verbose = True

    known_indexers = find_indexers(ascii_binder_search.indexers)

    if args.indexer not in known_indexers:
        print("Unknown indexer {}".format(args.indexer))
        sys.exit(1)
    indexer = known_indexers[args.indexer](verbose, static_dir)
    if os.path.isdir(os.path.join(static_dir, args.indexer)):
        indexer.backend_static_dir = args.indexer
    indexer.run()

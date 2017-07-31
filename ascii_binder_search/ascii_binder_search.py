""" This is a small plugin that can be used to implement search in your asciibinder project. """

import os
import sys
import json
from shutil import copyfile
import argparse
from collections import defaultdict

import yaml
import xmltodict
from bs4 import BeautifulSoup
import codecs
import pkg_resources


dist = pkg_resources.get_distribution('ascii_binder_search')

static_dir = os.path.join(dist.location, 'ascii_binder_search/static')

verbose = False


def is_packaged():
    """ Checks if the documentation is packaged """
    return "_package" in os.listdir('.')


def repo_check():
    """ Checks if it's a valid ascii_binder compitable repo """
    ls = os.listdir('.')
    if '_distro_map.yml' not in ls or '_distro_map.yml' not in ls:
        print("The specified docs base directory {} does"
              "not appear to be a valid ascii_binder directory."
              .format(os.getcwd()))
        return False

    return True


def generate_package():
    """ Runs asciibinder command to package the docs """
    os.system('ascii_binder package')


def distro_exists(distro):
    return distro in os.listdir('_package')


def find_and_parse_sitemap(distro):
    sitemap = open('_package/{}/sitemap.xml'.format(distro))
    return xmltodict.parse(sitemap.read())


def parse_html_doc(path):
    """ Parses the title and the main article and returns it as dict """
    try:
        doc_file = codecs.open(path, 'r')
        soup = BeautifulSoup(doc_file.read(), "lxml")
        title = soup.find('title').get_text()
        ptags = soup.findAll('div', class_="paragraph")
        content = ''
        for p in ptags:
            content += p.get_text()
        return {"title": title, "content": content}
    except IndexError:
        return None


def copy_static_assets(path):
    """ Copies the static assets to their respective directory.
    Please make sure that
    """
    # create _javascripts folder under the site folder if not exists
    if not os.path.exists(path + '_javascripts'):
        os.mkdir(path + '_javascripts', 0o777)
    contents = os.listdir(static_dir)
    for asset_path in contents:
        dest = path
        if '.css' in asset_path:
            dest += '_stylesheets'
        elif '.js' in asset_path:
            dest += '_javascripts'

        copyfile(os.path.join(static_dir, asset_path), os.path.join(dest, asset_path))
        if verbose:
            print("Copied {} to {}".format(asset_path, dest))


def generate_dump():
    """ Generates json file for each and every distros """
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
                doc_content = parse_html_doc('_package' + '/' + site_folder + '/' + topic_path)
                version = topic_path[:topic_path.index('/')]
                if doc_content:
                    data[version].append({
                        "topic_url": topic_path,
                        "title": doc_content['title'],
                        "content": doc_content['content'],
                        "site_name": site_name
                    })
            for version in data:
                dump_file = open('{}/data_{}.json'.format('_package/' + site_folder + '/',
                                                          version), 'w+')
                json.dump(data[version], dump_file)
                dump_file.close()
                if verbose:
                    print("File Created in: " + os.path.realpath(dump_file.name))

            copy_static_assets('_package/{}/'.format(site_folder))
            versions_file = open('{}/versions.json'.format('_package/' + site_folder + '/'), 'w+')
            json.dump({"versions": list(data.keys())}, versions_file)
            versions_file.close()

            if verbose:
                print("File Created in: " + os.path.realpath(versions_file.name))


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
    parser.add_argument('-s', '--static-dir')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.static_dir:
        static_dir = args.static_dir

    if args.verbose:
        verbose = True

    generate_dump()


if __name__ == '__main__':
    main()

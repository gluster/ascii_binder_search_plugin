""" This is a small plugin that can be used to implement search in your asciibinder project. """

import os
import sys
import json
from shutil import copyfile
import argparse

import yaml
import xmltodict
from bs4 import BeautifulSoup
import codecs
import pkg_resources


dist = pkg_resources.get_distribution('ascii_binder_search')

search_file_path = os.path.join(dist.location, 'static/search.html')

def is_packaged():
    """ Checks if the documentation is packaged """
    return "_package" in os.listdir()


def repo_check():
    """ Checks if it's a valid ascii_binder compitable repo """
    ls = os.listdir()

    if '_distro_map.yml' not in ls or '_distro_map.yml' not in ls:
        print("The specified docs base directory {} does not appear to be a valid ascii_binder directory.".format(os.getcwd())) #  noqa
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


def generate_dump():
    """ Generates json file for each and every distros """
    with open('_distro_map.yml') as distro_map_yml:
        distro_map = yaml.load(distro_map_yml)
        for distro in distro_map:
            site_folder = distro_map[distro]['site']
            data = []
            if not distro_exists(site_folder):
                continue
            sitemap = find_and_parse_sitemap(site_folder)
            urls = sitemap['urlset']['url']
            site_name = urls[0]['loc']
            for url in urls[2:]:
                topic_url = '_package' + '/' + site_folder + '/' + url['loc'].replace(site_name, "")
                doc_content = parse_html_doc(topic_url)
                if doc_content:
                    data.append({
                        "topic_url": url['loc'].replace(site_name, ""),
                        "title": doc_content['title'],
                        "content": doc_content['content'],
                        "site_name": site_name
                    })
            data_json = open('{}/data.json'.format('_package/'+site_folder+'/'), 'w+')
            json.dump(data, data_json)
            copyfile(search_file_path, '_package/{}/search.html'.format(site_folder))
            data_json.close()


def main():
    global search_file_path
    if not repo_check():
        sys.exit(1)
    if not is_packaged():
        answer = input("Site must be packaged before generating docs. Would you like to package it? [Y/N] ")
        if answer in ['Y', 'y', 'yes']:
            os.system('asciibinder package')
        else:
            sys.exit()

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--search-template')
    args = parser.parse_args()

    if args.search_template:
        search_file_path = os.getcwd() + '/' + args.search_template

    generate_dump()


if __name__ == '__main__':
    main()

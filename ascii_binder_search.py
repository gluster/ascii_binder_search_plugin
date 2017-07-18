""" This is a small plugin that can be used to implement search in your asciibinder project. """

import os
import sys
import json

import yaml
import xmltodict
from lxml import html
import codecs



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
    doc_file = codecs.open(path, 'r')
    doc = html.fromstring(doc_file.read().replace('\n', ""))
    title = doc.xpath("//title")[0].text_content()
    ptags = doc.xpath("//div[contains(@class, 'paragraph')]")
    content = ''
    for p in ptags:
        content += p.text_content() + '\n'
    return {"title": title, "content": content}


def generate_dump():
    """ Generates json file for each and every distros """
    with open('_distro_map.yml') as distro_map_yml:
        distro_map = yaml.load(distro_map_yml)
        for distro in distro_map:
            data = []
            if not distro_exists(distro):
                continue
            sitemap = find_and_parse_sitemap(distro)
            urls = sitemap['urlset']['url']
            site_name = urls[0]['loc']
            for url in urls[2:]:
                topic_url = '_package' + '/' + distro + url['loc'].replace(site_name, "")
                doc_content = parse_html_doc(topic_url)
                data.append({
                    "topic_url": topic_url,
                    "title": doc_content['title'],
                    "content": doc_content['content'],
                })
            data_json = open('{}/data.json'.format('_package/'+distro+'/'), 'w+')
            json.dump(data, data_json)
            data_json.close()


def main():
    if not repo_check():
        sys.exit(1)
    if not is_packaged():
        answer = input("Site must be packaged before generating docs. Would you like to package it? [Y/N] ")
        if answer in ['Y', 'y', 'yes']:
            os.system('asciibinder package')
        else:
            sys.exit()
    generate_dump()


if __name__ == '__main__':
    main()

""" All utility functions are present here """


import os
from shutil import copyfile

import xmltodict


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
    """ Checks if the distro folder exists or not """
    return distro in os.listdir('_package')


def find_and_parse_sitemap(distro):
    sitemap = open('_package/{}/sitemap.xml'.format(distro))
    return xmltodict.parse(sitemap.read())


def copy_static_assets(path, static_dir, verbose):
    """ Copies the static assets to their respective directory.
    Please make sure that
    """
    # create _javascripts folder under the site folder if not exists
    if not os.path.exists(path + '_javascripts'):
        os.mkdir(path + '_javascripts', 0o777)
    contents = []
    for asset in os.listdir(static_dir):
        if os.path.isfile(os.path.join(static_dir, asset)):
            contents.append(asset)
    for asset_path in contents:
        dest = path
        if '.css' in asset_path:
            dest += '_stylesheets'
        elif '.js' in asset_path:
            dest += '_javascripts'

        copyfile(os.path.join(static_dir, asset_path), os.path.join(dest, asset_path))
        if verbose:
            print("Copied {} to {}".format(asset_path, dest))

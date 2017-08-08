import os
import json

from ascii_binder_search.indexer import Indexer


class FrontEndIndexer(Indexer):
    def index(self, dump, distro, site_folder):
        for version in dump:
            dump_file = open('{}/data_{}.json'.format('_package/' + site_folder + '/',
                             version), 'w+')
            json.dump(dump[version], dump_file)
            dump_file.close()
            if self.verbose:
                print("File Created in: " + os.path.realpath(dump_file.name))

        versions_file = open('{}/versions.json'.format('_package/' + site_folder + '/'), 'w+')
        json.dump({"versions": list(dump.keys())}, versions_file)
        versions_file.close()

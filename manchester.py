#!/usr/bin/env python2
import errno
import fuse
import optparse
import os
import stat
import yaml

fuse.fuse_python_api = (0, 2)

def mkdir(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)

class Pool:
    def __init__(self, mountpoint):
        self.sources = []
        self.shares = []
        self.mountpoint = mountpoint

    def add_source(self, source):
        for share in self.shares:
            source.add_share(share)
        self.sources.append(source)

    def add_share(self, share):
        for source in self.sources:
            source.add_share(share)
        self.shares.append(share)

class Source:
    def __init__(self, directory):
        self.directory = directory

    def add_share(self, share):
        mkdir("{0}/{1}".format(self.get_directory(), share.get_name()))

    def get_directory(self):
        return self.directory

class Share:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

class PoolFs(fuse.Fuse):
    def __init__(self, pool, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.pool = pool

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-c", "--config",
            help="Configuration File",
            dest="config"
    )
    (options, arguments) = parser.parse_args()

    if options.config is None:
        options.config = 'configuration.yaml'

    config = yaml.load(open(options.config).read())

    pool = Pool(config["mount"])
    for source_directory in config["sources"]:
        pool.add_source(Source(source_directory))
    for share_name in config["shares"]:
        pool.add_share(Share(share_name))

    pool_fs = PoolFs(pool)
    pool_fs.parse(errex=1)
    pool_fs.main()

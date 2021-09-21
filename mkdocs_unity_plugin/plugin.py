import os
import json
import logging
from tempfile import mktemp, mkdtemp

from mkdocs.config import config_options, load_config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import get_files, Files, File

logger = logging.getLogger(__name__)


class UnityPlugin(BasePlugin):
    config_scheme = (
        ('sites', config_options.Type(list, default=[])),
    )

    def __init__(self):
        self._sub_sites = {}
        self._extra_watches = []
        self.tmp_docs_dir = None

    @property
    def sub_sites(self):
        if not self._sub_sites:
            for sub_site in self.config["sites"]:
                if not isinstance(sub_site, dict):
                    sub_site = {sub_site: {}}
                self._sub_sites.update(**sub_site)
        for k, v in self._sub_sites.items():
            v.setdefault('mountpoint', k)
            yield k, v

    def on_config(self, config):
        if not self.tmp_docs_dir:
            self.tmp_docs_dir = mkdtemp(prefix='mkdocs-unity')
        tmp_docs_dir = self.tmp_docs_dir
        parent_docs_dir = os.path.join(tmp_docs_dir, config['site_name'].replace(' ', '-'))
        if not os.path.isdir(parent_docs_dir):
            os.symlink(config['docs_dir'], parent_docs_dir)

        for site_name, site_config in self.sub_sites:
            sub_site_rel_path = site_config.get('path', site_name)

            # Get target mkdocs config
            sub_config = load_config(os.path.join(config['docs_dir'], os.path.pardir, sub_site_rel_path, 'mkdocs.yml'))

            sub_site_dest_path = os.path.join(parent_docs_dir, site_config['mountpoint'])
            destination_parent = os.path.realpath(os.path.join(sub_site_dest_path, os.pardir))
            if not os.path.isdir(destination_parent):
                os.makedirs(destination_parent)
            if not os.path.isdir(sub_site_dest_path):
                os.symlink(sub_config['docs_dir'], sub_site_dest_path)

        config['docs_dir'] = parent_docs_dir
        return config

    def disabled_on_files(self, files, config):
        initial_docs_dir = config["docs_dir"]
        for site_name, site_config in self.sub_sites:
            sub_site_rel_path = site_config.get('path', site_name)
            sub_site_dest_path = site_config['mountpoint']

            # Get target mkdocs config
            sub_config = load_config(os.path.join(initial_docs_dir, os.path.pardir, sub_site_rel_path, 'mkdocs.yml'))

            # Update global config with sub_site docs_dir
            config["docs_dir"] = os.path.join(sub_config["docs_dir"], os.path.pardir)

            self._extra_watches.append(sub_config["docs_dir"])
            sub_site_files = get_files(config)

            # Remove files that aren't in sub_config["docs_dir"] and fix destination/URL pathing
            for f in sub_site_files:
                if os.path.commonpath([sub_config["docs_dir"], f.abs_src_path]) != sub_config['docs_dir']:
                    continue
                for attr in ['abs_dest_path', 'dest_path', 'url']:
                    setattr(f, attr, getattr(f, attr).replace('docs/', f"{sub_site_dest_path}/"))
                setattr(f, 'src_path', getattr(f, 'src_path').replace('docs/', f"{sub_site_rel_path}/"))
                files.append(f)

        config["docs_dir"] = os.path.realpath(os.path.join(initial_docs_dir, os.path.pardir))

    def on_serve(self, server, config, builder):
        for x in self._extra_watches:
            server.watch(x)

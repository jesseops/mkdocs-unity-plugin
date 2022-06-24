import os
import json
import logging

from mkdocs.config import config_options, load_config, Config
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

    @property
    def sub_sites(self):
        if not self._sub_sites:
            for site in self.config["sites"]:
                if not isinstance(site, dict):
                    site = {site: {}}
                name, config = site.popitem()
                config.setdefault('path', name)
                config.setdefault('mountpoint', self._get_site_config(config['path'])['site_name'] or name)
                config['mountpoint'] = config['mountpoint'].replace(' ', '-')
                self._sub_sites[name] = config
        return self._sub_sites

    def _get_site_config(self, site_path: str):
        global_config = load_config(self.config.config_file_path)
        return load_config(os.path.join(global_config['docs_dir'], os.path.pardir, site_path, 'mkdocs.yml'))

    @staticmethod
    def _fix_nav_entries(nav, relpath=''):
        if isinstance(nav, list):
            return [UnityPlugin._fix_nav_entries(x, relpath=relpath) for x in nav]
        if isinstance(nav, dict):
            for k, v in nav.items():
                nav[k] = UnityPlugin._fix_nav_entries(v, relpath=relpath)
            return nav
        if isinstance(nav, str):
            if relpath:
                nav = f"{relpath}/{nav}"
            return nav
        return nav

    def on_config(self, config: Config):
        if config['nav']:
            for site, site_config in self.sub_sites.items():
                site_mkdocs_config = self._get_site_config(site_config['path'])
                if site_mkdocs_config['nav']:
                    config['nav'].append(
                        {site_config['mountpoint']: self._fix_nav_entries(site_mkdocs_config['nav'],
                                                                          site_config['path'])})
                logger.info(f"Got sub-site mkdocs at {site_mkdocs_config}")
        return config

    def on_files(self, files, config):
        initial_docs_dir = config["docs_dir"]
        for site_name, site_config in self.sub_sites.items():
            sub_site_rel_path = site_config.get('path', site_name)
            sub_site_dest_path = site_config['mountpoint']

            # Get target mkdocs config
            sub_config = self._get_site_config(site_config['path'])

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

        config["docs_dir"] = initial_docs_dir

    def on_serve(self, server, config, builder):
        for x in self._extra_watches:
            server.watch(x)

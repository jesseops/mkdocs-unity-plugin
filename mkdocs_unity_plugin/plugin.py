import logging
import os

from mkdocs.config import config_options, load_config, Config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import get_files
from mkdocs.utils import dirname_to_title

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

                site_mkdocs_config = self._get_site_config(config['path'])

                config.setdefault('include_in_nav', False)
                config.setdefault('use_site_name_as_title', False)
                config.setdefault('mountpoint', site_mkdocs_config.get('site_name', name))

                config['mountpoint'] = config['mountpoint'].replace(' ', '-')

                if config['use_site_name_as_title']:
                    config['title'] = dirname_to_title(site_mkdocs_config['site_name']).title()
                else:
                    config.setdefault('title', dirname_to_title(config['mountpoint']).title())
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
            nav = nav.strip()
            if relpath:
                # awesome-pages plugin support
                if nav == "...":
                    return os.path.join(f"... | glob={relpath}", "**/*.md")
                if navsplit := nav.split("glob=", 1):
                    return os.path.join(f"... | glob={relpath}", navsplit[-1])
                nav = os.path.join(relpath, nav)
            return nav
        return nav

    def on_config(self, config: Config):
        if config['nav']:
            for site, site_config in self.sub_sites.items():
                site_mkdocs_config = self._get_site_config(site_config['path'])
                if site_config['include_in_nav'] is True and site_mkdocs_config['nav']:
                    config['nav'].append(
                        {site_config['title']: self._fix_nav_entries(site_mkdocs_config['nav'],
                                                                     site_config['path'])})
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
            self._extra_watches.append(sub_config.config_file_path)
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

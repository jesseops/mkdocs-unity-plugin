import os
import json
import logging

from mkdocs.config import config_options, load_config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import get_files, Files, File

logger = logging.getLogger(__name__)


class UnityPlugin(BasePlugin):
    config_scheme = (
        ('sites', config_options.Type(list, default=[])),
    )

    def on_config(self, config, **kwargs):
        pass

    def on_nav(self, nav, **kwargs):
        pass

    def on_files(self, files, config):
        initial_docs_dir = config["docs_dir"]
        for sub_site in self.config["sites"]:
            # Get target mkdocs config
            sub_config = load_config(os.path.join(initial_docs_dir, os.path.pardir, sub_site, 'mkdocs.yml'))
            config["docs_dir"] = os.path.join(sub_config["docs_dir"], os.path.pardir)
            sub_site_files = get_files(config)
            # Remove files that aren't in sub_config["docs_dir"] and fix destination/URL pathing
            for f in sub_site_files:
                if os.path.commonpath([sub_config["docs_dir"], f.abs_src_path]) != sub_config['docs_dir']:
                    continue
                for attr in ['abs_dest_path', 'dest_path', 'src_path', 'url']:
                    setattr(f, attr, getattr(f, attr).replace('docs', sub_site))
                files.append(f)

        config["docs_dir"] = initial_docs_dir

    def on_page_read_source(self, page, config):
        pass

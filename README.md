# mkdocs-unity-plugin
Simple MkDocs plugin to unify multiple docs repos

> Note: this is currently very much alpha software

The goal is to permit unifying multiple MkDocs repos while allowing each flexibility and avoiding interference with
other plugins.

## Usage

Create a parent MkDocs project, checkout other MkDocs projects in the root repo. Add the `unity` plugin to your list
of installed plugins in the parent projects `mkdocs.yml` and reference the `sites`.

At present, no configuration from the sub-site docs will be respected/handled. I'd like to at least make this work
nicely with the awesome-pages plugin; I'll need to determine whether to go complex and perform multiple
rendering iterations or just go simple and assume if a docs repo is being adopted it should only rely on
configuration from the parent.

### Example

#### Installation
```bash
pip install git+https://github.com/jesseops/mkdocs-unity-plugin.git
```

#### Configuration
```yaml
#mkdocs.yaml
...
plugins:
  - search
  - unity:
      sites:
        - site1
        - site2
...
```
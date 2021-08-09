# mkdocs-unity-plugin
Simple MkDocs plugin to unify multiple docs repos

> Note: this is currently very much alpha software

The goal is to permit unifying multiple MkDocs repos while allowing each flexibility and avoiding interference with
other plugins.

## Usage

Create a parent MkDocs project, checkout other MkDocs projects in the root repo. Add the `unity` plugin to your list
of installed plugins in the parent projects `mkdocs.yml` and reference the `sites`.

This plugin currently works (on my box) with normal builds as well as live/gh-deploy. With the `awesome-pages` plugin
installed and activated _after_ `unity`, both normal & _awesome_ nav work. Note: you must define custom navigation in
the child projects using `.page` or similar files as the child `mkdocs.yml` is not evaluated.

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
      - site1:
          mountpoint: "sub-path/or-even-nestedhere"
      - site2:
          mountpoint: "Site 2"
            path: "./submodules/site-2"
      - site3
...
```
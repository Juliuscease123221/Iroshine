# Contributing

Issues and pull requests are welcome at
[github.com/Juliuscease123221/Iroshine](https://github.com/Juliuscease123221/Iroshine).

## Set up

```bash
git clone https://github.com/Juliuscease123221/Iroshine.git
cd Iroshine
python -m venv .venv && source .venv/bin/activate
pip install -e . "mkdocs>=1.6,<2" "mkdocs-material>=9.5,<10"
```

## Check a change

There is no automated test suite yet. Before opening a pull request, render the examples your change
could affect as drafts and watch them:

```bash
cd examples
python 00_start_here.py low
```

Two rules keep old videos working:

- **New behaviour is opt-in.** Add a parameter whose default reproduces the old behaviour.
- **Describe every option beside its field.** The reference is generated from those comments.

## Work on the docs

```bash
python tools/gen_reference.py      # rebuild docs/reference/ from the source
mkdocs serve                       # preview at http://127.0.0.1:8000
```

The site is rebuilt and published automatically on every push to `main`.

| To change… | Edit |
|---|---|
| a guide or tutorial | the Markdown file under `docs/` |
| an option's description | the comment beside the field in `iroshine/*.py` |
| which objects appear on which reference page | `PAGES` in `tools/gen_reference.py` |
| the gallery | `docs/gallery.md` and the videos in `docs/assets/videos/` |

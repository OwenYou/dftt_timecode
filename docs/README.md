# Documentation

This directory contains the Sphinx documentation for dftt_timecode.

## Building Documentation Locally

### Prerequisites

Install the required dependencies:

```bash
pip install sphinx pydata-sphinx-theme
```

### Build HTML Documentation

On Unix/macOS:

```bash
cd docs
make html
```

On Windows:

```bash
cd docs
make.bat html
```

The built documentation will be available in `docs/_build/html/`.

### View Documentation

Open `docs/_build/html/index.html` in your web browser.

### Other Build Formats

```bash
make latexpdf  # Build PDF (requires LaTeX)
make epub      # Build EPUB
make help      # See all available formats
```

## Automatic Deployment

Documentation is automatically built and deployed to GitHub Pages when changes are pushed to the main branch.

The deployment is handled by the GitHub Actions workflow in `.github/workflows/docs.yml`.

## Documentation Structure

- `index.rst` - Home page
- `installation.rst` - Installation instructions
- `quickstart.rst` - Quick start guide
- `user_guide.rst` - Comprehensive user guide
- `api/` - API reference documentation
- `contributing.rst` - Contributing guidelines
- `changelog.rst` - Version history
- `conf.py` - Sphinx configuration
- `_static/` - Static files (CSS, images, etc.)
- `_templates/` - Custom templates

## Writing Documentation

- Documentation is written in reStructuredText (RST) format
- API documentation is auto-generated from docstrings using Sphinx autodoc
- Follow the existing style and structure when adding new pages
- Build and preview locally before committing changes

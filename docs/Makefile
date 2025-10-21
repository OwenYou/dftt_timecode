# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# i18n settings
LANGUAGES     = en zh_CN

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo ""
	@echo "i18n targets:"
	@echo "  gettext      to generate .pot files for translation"
	@echo "  update-po    to update .po files from .pot files"
	@echo "  html-all     to build HTML documentation for all languages"
	@echo "  html-zh      to build HTML documentation for Chinese only"

.PHONY: help Makefile gettext update-po html-all html-zh

# Generate .pot files for translation
gettext:
	@$(SPHINXBUILD) -b gettext "$(SOURCEDIR)" "$(BUILDDIR)/gettext" $(SPHINXOPTS) $(O)
	@echo "Build finished. The message catalogs are in $(BUILDDIR)/gettext."

# Update .po files from .pot files
update-po: gettext
	sphinx-intl update -p "$(BUILDDIR)/gettext" -l zh_CN
	@echo "Update finished. Translation files are in locale/zh_CN/LC_MESSAGES/."

# Build HTML documentation for all languages
html-all:
	@echo "Building English documentation..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo "Building Chinese documentation..."
	@$(SPHINXBUILD) -b html -D language=zh_CN "$(SOURCEDIR)" "$(BUILDDIR)/html/zh_CN" $(SPHINXOPTS) $(O)
	@echo ""
	@echo "Build finished. HTML documentation for all languages is in $(BUILDDIR)/html/."

# Build HTML documentation for Chinese only
html-zh:
	@echo "Building Chinese documentation..."
	@$(SPHINXBUILD) -b html -D language=zh_CN "$(SOURCEDIR)" "$(BUILDDIR)/html/zh_CN" $(SPHINXOPTS) $(O)
	@echo ""
	@echo "Build finished. Chinese HTML documentation is in $(BUILDDIR)/html/zh_CN/."

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

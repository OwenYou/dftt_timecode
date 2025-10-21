Contributing
============

We welcome contributions to dftt_timecode! This guide will help you get started.

Getting Started
---------------

1. Fork the repository on GitHub
2. Clone your fork locally:

   .. code-block:: bash

      git clone https://github.com/YOUR_USERNAME/dftt_timecode.git
      cd dftt_timecode

Development Workflow
--------------------

Setting Up Your Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a virtual environment and install dependencies:

.. code-block:: bash

   uv sync

This command will:

- Create a virtual environment (if not already present)
- Install all dependencies from ``pyproject.toml``
- Install the package in editable mode
- Generate/update ``uv.lock`` for reproducible builds

Running Tests
~~~~~~~~~~~~~

Run all tests:

.. code-block:: bash

   uv run pytest

Run tests with verbose output:

.. code-block:: bash

   uv run pytest -v -s

Run specific test file:

.. code-block:: bash

   uv run pytest test/test_dftt_timecode.py

Code Style
----------

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and concise

Writing Tests
-------------

All new features and bug fixes should include tests:

.. code-block:: python

   import pytest
   from dftt_timecode import DfttTimecode

   def test_new_feature():
       tc = DfttTimecode('01:00:00:00', 'auto', fps=24)
       # Test your feature
       assert tc.some_new_method() == expected_result

Documentation
-------------

Update documentation when adding new features:

1. Add docstrings to your code
2. Update relevant .rst files in the docs/ directory
3. Build documentation locally to verify:

   .. code-block:: bash

      cd docs
      uv run make html

Contributing Translations
~~~~~~~~~~~~~~~~~~~~~~~~~

We welcome contributions to documentation translations! Currently we support:

- **English** (primary language)
- **中文 (Simplified Chinese)**

How to Contribute Translations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Adding new translations to existing languages:**

1. Navigate to the translation files:

   .. code-block:: bash

      cd docs/locale/zh_CN/LC_MESSAGES/

2. Edit the ``.po`` files to add or improve translations:

   .. code-block:: po

      #: ../../quickstart.rst:2
      msgid "Quick Start"
      msgstr "快速开始"

3. Build and preview your translations:

   .. code-block:: bash

      cd docs
      uv run make html-zh      # Build Chinese only
      uv run make html-all     # Build all languages

4. Preview locally:

   .. code-block:: bash

      cd docs/_build/html
      python -m http.server 8000
      # Visit http://localhost:8000/zh_CN/

**Adding a new language:**

1. Generate translation files for your language:

   .. code-block:: bash

      cd docs
      uv run sphinx-intl update -p _build/gettext -l <LANG_CODE>
      # e.g., for Japanese: -l ja

2. Update ``docs/Makefile`` to include the new language in the ``LANGUAGES`` variable

3. Update ``docs/_static/switcher.json`` to add your language option

4. Update the language switcher template in ``docs/_templates/language-switcher.html``

5. Translate the ``.po`` files in ``locale/<LANG_CODE>/LC_MESSAGES/``

6. Build and test your translation

**Translation Guidelines:**

- **User documentation** (installation, quickstart, user guide): Translate everything
- **API documentation**: Translate page titles and main descriptions, but keep technical details (class names, method names, parameters) in English
- **Changelog**: Translate section headers, but keep technical change entries in English
- **Code examples**: Keep code and variable names in English
- **Technical terms**: Use consistent translations (see the translation guide in ``docs/I18N_README.md``)

**Updating translations when source changes:**

When documentation source files are updated, translations need to be updated:

.. code-block:: bash

   cd docs
   uv run make gettext        # Generate new translation templates
   uv run make update-po      # Update .po files with new strings
   # Edit .po files to translate new or updated strings
   uv run make html-all       # Rebuild documentation

**Translation System Overview**

The project uses Sphinx with ``sphinx-intl`` for internationalization. The system uses gettext ``.po`` (Portable Object) files for translations, which is the industry standard for software localization.

**File Structure:**

::

   docs/
   ├── locale/                      # Translation files directory
   │   └── zh_CN/
   │       └── LC_MESSAGES/
   │           ├── index.po         # Translations for index.rst
   │           ├── quickstart.po
   │           ├── user_guide.po
   │           └── api/
   │               ├── dftt_timecode.po
   │               ├── dftt_timerange.po
   │               └── error.po
   ├── _build/
   │   └── gettext/                 # Generated .pot template files (don't commit)
   └── _templates/
       └── language-switcher.html   # Language switcher dropdown widget

**Detailed Translation Workflow:**

1. **Generate translation templates** (when source docs change):

   .. code-block:: bash

      cd docs
      uv run make gettext

   This creates ``.pot`` files in ``_build/gettext/`` containing all translatable strings.

2. **Update translation files**:

   .. code-block:: bash

      cd docs
      uv run make update-po

   This updates ``.po`` files in ``locale/zh_CN/LC_MESSAGES/`` with new strings while preserving existing translations.

3. **Translate the strings**:

   Open ``.po`` files and add translations:

   .. code-block:: po

      #: ../../index.rst:70
      msgid "User Guide"
      msgstr "用户指南"

      #: ../../index.rst:78
      msgid "API Reference"
      msgstr "API 参考"

   **Translation Tips:**

   - Each ``msgid`` contains the original English text
   - Add your translation in the corresponding ``msgstr`` field
   - Preserve formatting codes like ``{0}``, ``%s``, etc.
   - Keep technical terms (class/function names) untranslated
   - Use tools like `Poedit <https://poedit.net/>`_ for easier editing

4. **Build and test**:

   .. code-block:: bash

      cd docs
      uv run make html-zh      # Build Chinese only
      uv run make html-all     # Build all languages

   Preview the result:

   .. code-block:: bash

      cd docs/_build/html
      python -m http.server 8000
      # Visit http://localhost:8000/zh_CN/

5. **Commit your changes**:

   .. code-block:: bash

      git add locale/
      git commit -m "Update Chinese translation for user guide"

**Important Makefile Commands:**

- ``make gettext``: Generate ``.pot`` template files from source ``.rst`` files
- ``make update-po``: Update ``.po`` files from ``.pot`` templates
- ``make html``: Build English documentation only
- ``make html-zh``: Build Chinese documentation only
- ``make html-all``: Build all language versions

**Common Issues and Solutions:**

**Translations not showing:**

1. Ensure ``.po`` files have non-empty ``msgstr`` values
2. Rebuild with ``uv run make html-all``
3. Clear browser cache or use incognito mode

**New strings not appearing in .po files:**

1. Run ``uv run make gettext`` to regenerate ``.pot`` files
2. Run ``uv run make update-po`` to update ``.po`` files
3. Check that your source ``.rst`` files are included in the build

**Language switcher not working:**

1. Verify ``_templates/language-switcher.html`` exists
2. Ensure target language HTML was built in correct subdirectory (``_build/html/zh_CN/``)

**Best Practices:**

- **Commit ``.po`` files**: Always commit updated ``.po`` files to version control
- **Don't commit ``.pot`` files**: These are generated artifacts in ``_build/gettext/``
- **Incremental translation**: It's okay to commit partially translated ``.po`` files; untranslated strings display in English
- **Review before push**: Build and preview locally before pushing translations
- **Consistent terminology**: Use consistent translations for technical terms across all pages
- **Keep source in sync**: Run ``make update-po`` regularly to sync with source changes

**Automated Deployment:**

Documentation is automatically built and deployed via GitHub Actions when pushed to ``main``:

- Workflow: ``.github/workflows/docs.yml``
- Build command: ``uv run make html-all``
- Deployment: GitHub Pages at https://owenyou.github.io/dftt_timecode/

When you push translated ``.po`` files to the ``main`` branch (via ``dev`` merge), the multilingual documentation is automatically rebuilt and deployed.

**Additional Resources:**

- `Sphinx Internationalization <https://www.sphinx-doc.org/en/master/usage/advanced/intl.html>`_
- `sphinx-intl Documentation <https://sphinx-intl.readthedocs.io/>`_
- `GNU gettext Documentation <https://www.gnu.org/software/gettext/manual/>`_

Submitting Changes
------------------

1. Create a new branch for your changes:

   .. code-block:: bash

      git checkout -b feature/my-new-feature

2. Make your changes and commit:

   .. code-block:: bash

      git add .
      git commit -m "Add new feature: description"

3. Push to your fork:

   .. code-block:: bash

      git push origin feature/my-new-feature

4. Open a Pull Request on GitHub

Pull Request Guidelines
-----------------------

- Provide a clear description of the changes
- Reference any related issues
- Ensure all tests pass
- Update documentation as needed
- Keep changes focused and atomic

Reporting Bugs
--------------

When reporting bugs, please include:

- Python version
- dftt_timecode version
- Minimal code example that reproduces the issue
- Expected vs actual behavior
- Any error messages or stack traces

Feature Requests
----------------

Feature requests are welcome! Please provide:

- Clear description of the feature
- Use cases and examples
- Why this would be valuable to other users

Code of Conduct
---------------

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

License
-------

By contributing, you agree that your contributions will be licensed under the
GNU Lesser General Public License v2 (LGPLv2).

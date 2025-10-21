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
      uv run sphinx-build -b html . _build

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

Installation
============

Requirements
------------

- Python >= 3.11
- Standard library dependencies only (no external dependencies required)

  - fractions
  - logging
  - math
  - functools
  - re

Installation from PyPI
----------------------

The easiest way to install dftt_timecode is using pip or uv:

.. code-block:: bash

   # Using pip
   pip install dftt_timecode

   # Using uv (recommended)
   uv pip install dftt_timecode

Installation from Source
-------------------------

For development, we recommend using **uv** for faster and more reliable dependency management:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/OwenYou/dftt_timecode.git
   cd dftt_timecode

   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Sync dependencies and install in development mode
   uv sync

This will:

- Create a virtual environment in ``.venv``
- Install all development dependencies (pytest, sphinx, etc.)
- Install the package in editable mode

Alternatively, using pip:

.. code-block:: bash

   git clone https://github.com/OwenYou/dftt_timecode.git
   cd dftt_timecode
   pip install -e .

Verifying Installation
-----------------------

You can verify the installation by importing the package:

.. code-block:: python

   import dftt_timecode
   print(dftt_timecode.__version__)

Development Dependencies
------------------------

The project uses **uv** for dependency management. All dependencies are defined in ``pyproject.toml``:

- **pytest** - Testing framework
- **sphinx** - Documentation generator
- **pydata-sphinx-theme** - Documentation theme

To install development dependencies with uv:

.. code-block:: bash

   # Install all development dependencies
   uv sync

   # Activate the virtual environment
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

To run tests:

.. code-block:: bash

   pytest

To build documentation:

.. code-block:: bash

   cd docs
   make html

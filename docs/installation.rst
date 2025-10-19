Installation
============

Requirements
------------

- Python >= 3.11
- Standard library dependencies:

  - fractions
  - logging
  - math
  - functools
  - re

Installation from PyPI
----------------------

The easiest way to install dftt_timecode is using pip:

.. code-block:: bash

   pip install dftt_timecode

Installation from Source
-------------------------

To install from source, clone the repository and install in development mode:

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

Dependencies
------------

For development, you may want to install additional dependencies:

.. code-block:: bash

   pip install -r requirements.txt

This includes:

- pytest for testing
- sphinx for documentation
- pydata-sphinx-theme for documentation theme

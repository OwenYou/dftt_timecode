dftt_timecode
=============

.. image:: https://img.shields.io/badge/pypi-0.0.14-brightgreen
   :target: https://pypi.org/project/dftt-timecode/
   :alt: PyPI

.. image:: https://img.shields.io/badge/python-3-blue
   :alt: Python 3

.. image:: https://img.shields.io/badge/license-LGPL2.1-green
   :target: https://github.com/OwenYou/dftt_timecode/blob/main/LICENSE
   :alt: License

Python timecode library for film and TV industry, with high frame rate support and comprehensive features.

为影视行业设计的Python时码库，支持HFR高帧率以及其他丰富的功能。

DFTT stands for the Department of Film and TV Technology of Beijing Film Academy.

Features
--------

- **Multiple Timecode Format Support**: SMPTE (DF/NDF), SRT, DLP (Cine Canvas), FFMPEG, FCPX, frame count, timestamp
- **High Frame Rate Support**: Supports frame rates from 0.01 to 999.99 fps
- **Drop-Frame/Non-Drop-Frame**: Strictly supports SMPTE DF/NDF formats
- **Extended Time Range**: Currently supports time range from -99 to 99 hours
- **Strict Mode**: 24-hour cycling mode that automatically converts timecodes outside the 0-24 hour range
- **High Precision**: Internal storage using high-precision Fraction timestamps for accurate conversions
- **Rich Operators**: Comprehensive support for arithmetic and comparison operations between timecodes and numbers

Installation
------------

.. code-block:: bash

   pip install dftt_timecode

Quick Start
-----------

.. code-block:: python

   from dftt_timecode import DfttTimecode

   # Create a timecode object
   tc = DfttTimecode('01:00:00:00', 'auto', fps=24, drop_frame=False, strict=True)

   # Access properties
   print(tc.type)          # 'smpte'
   print(tc.fps)           # 24
   print(tc.framecount)    # 86400
   print(tc.timestamp)     # 3600.0

   # Convert between formats
   print(tc.timecode_output('srt'))     # '01:00:00,000'
   print(tc.timecode_output('ffmpeg'))  # '01:00:00.00'

   # Arithmetic operations
   tc2 = DfttTimecode('00:30:00:00', 'auto', fps=24)
   result = tc + tc2
   print(result.timecode_output('smpte'))  # '01:30:00:00'

   # Comparison operations
   print(tc > tc2)  # True

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :titlesonly:

   installation
   quickstart
   user_guide

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   :titlesonly:

   api/dftt_timecode
   api/dftt_timerange
   api/error

.. toctree::
   :maxdepth: 1
   :caption: Development
   :titlesonly:

   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

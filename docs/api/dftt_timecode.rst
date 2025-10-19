DfttTimecode API
================

.. currentmodule:: dftt_timecode

.. autoclass:: DfttTimecode
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __str__, __repr__, __add__, __sub__, __mul__, __truediv__, __neg__, __eq__, __ne__, __lt__, __le__, __gt__, __ge__, __int__, __float__

Core Class
----------

The :class:`DfttTimecode` class is the main interface for working with timecodes in various formats.

Constructor
~~~~~~~~~~~

.. automethod:: DfttTimecode.__init__

Properties
~~~~~~~~~~

.. autoproperty:: DfttTimecode.type
.. autoproperty:: DfttTimecode.fps
.. autoproperty:: DfttTimecode.framecount
.. autoproperty:: DfttTimecode.timestamp
.. autoproperty:: DfttTimecode.is_drop_frame
.. autoproperty:: DfttTimecode.is_strict
.. autoproperty:: DfttTimecode.precise_timestamp

Methods
~~~~~~~

.. automethod:: DfttTimecode.set_fps
.. automethod:: DfttTimecode.set_type
.. automethod:: DfttTimecode.set_strict
.. automethod:: DfttTimecode.timecode_output

Operators
~~~~~~~~~

Arithmetic Operators
^^^^^^^^^^^^^^^^^^^^

.. automethod:: DfttTimecode.__add__
.. automethod:: DfttTimecode.__sub__
.. automethod:: DfttTimecode.__mul__
.. automethod:: DfttTimecode.__truediv__
.. automethod:: DfttTimecode.__neg__

Comparison Operators
^^^^^^^^^^^^^^^^^^^^

.. automethod:: DfttTimecode.__eq__
.. automethod:: DfttTimecode.__ne__
.. automethod:: DfttTimecode.__lt__
.. automethod:: DfttTimecode.__le__
.. automethod:: DfttTimecode.__gt__
.. automethod:: DfttTimecode.__ge__

Type Conversion Operators
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: DfttTimecode.__int__
.. automethod:: DfttTimecode.__float__
.. automethod:: DfttTimecode.__str__
.. automethod:: DfttTimecode.__repr__

Supported Timecode Types
-------------------------

The following timecode types are supported:

- **auto**: Automatic detection based on input format
- **smpte**: SMPTE timecode format (HH:MM:SS:FF or HH:MM:SS;FF for drop-frame)
- **srt**: SubRip subtitle format (HH:MM:SS,mmm)
- **ffmpeg**: FFmpeg format (HH:MM:SS.ff)
- **fcpx**: Final Cut Pro X format (frames/fps)
- **dlp**: DLP Cinema format (HH:MM:SS:FFF)
- **frame**: Frame count (integer)
- **time**: Timestamp in seconds (float)

Examples
--------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from dftt_timecode import DfttTimecode

   # Create a timecode
   tc = DfttTimecode('01:00:00:00', 'auto', fps=24, drop_frame=False, strict=True)

   # Access properties
   print(tc.framecount)  # 86400
   print(tc.timestamp)   # 3600.0

Format Conversion
~~~~~~~~~~~~~~~~~

.. code-block:: python

   tc = DfttTimecode('01:00:00:00', 'auto', fps=24)

   # Convert to different formats
   print(tc.timecode_output('srt'))     # '01:00:00,000'
   print(tc.timecode_output('ffmpeg'))  # '01:00:00.00'

Arithmetic Operations
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   tc1 = DfttTimecode('01:00:00:00', 'auto', fps=24)
   tc2 = DfttTimecode('00:30:00:00', 'auto', fps=24)

   # Add timecodes
   result = tc1 + tc2
   print(result.timecode_output('smpte'))  # '01:30:00:00'

   # Multiply by factor
   result = tc1 * 2
   print(result.timecode_output('smpte'))  # '02:00:00:00'

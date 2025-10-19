Quick Start
===========

This guide will help you get started with dftt_timecode quickly.

Importing the Library
---------------------

.. code-block:: python

   from dftt_timecode import DfttTimecode

Creating Timecode Objects
--------------------------

There are multiple ways to create timecode objects:

SMPTE Format
~~~~~~~~~~~~

.. code-block:: python

   # Non-drop-frame
   tc = DfttTimecode('01:00:00:00', 'auto', fps=24, drop_frame=False, strict=True)

   # Drop-frame (uses semicolon separator)
   tc_df = DfttTimecode('01:00:00;00', 'auto', fps=29.97, drop_frame=True)

Frame Count
~~~~~~~~~~~

.. code-block:: python

   # Using frame count with 'f' suffix
   tc = DfttTimecode('1000f', 'auto', fps=24)

   # Using integer (automatically treated as frame count)
   tc = DfttTimecode(1000, 'auto', fps=119.88, drop_frame=True)

Timestamp
~~~~~~~~~

.. code-block:: python

   # Using timestamp with 's' suffix
   tc = DfttTimecode('3600.0s', 'auto', fps=24)

   # Using float (automatically treated as timestamp)
   tc = DfttTimecode(3600.0, 'auto', fps=23.976)

   # Using Fraction for precise frame rates
   from fractions import Fraction
   tc = DfttTimecode(3600.0, 'auto', fps=Fraction(60000, 1001))

Other Formats
~~~~~~~~~~~~~

.. code-block:: python

   # SRT format
   tc = DfttTimecode('01:00:00,000', 'auto', fps=24)

   # FFMPEG format
   tc = DfttTimecode('01:00:00.00', 'auto', fps=24)

   # FCPX format
   tc = DfttTimecode('1/24s', 'auto', fps=24)

Accessing Timecode Properties
------------------------------

.. code-block:: python

   tc = DfttTimecode('01:00:00:00', 'auto', fps=24)

   print(tc.type)         # 'smpte'
   print(tc.fps)          # 24
   print(tc.framecount)   # 86400
   print(tc.timestamp)    # 3600.0
   print(tc.is_drop_frame)  # False
   print(tc.is_strict)    # True

Converting Between Formats
---------------------------

.. code-block:: python

   tc = DfttTimecode('01:00:00:00', 'auto', fps=24)

   # Convert to different formats
   print(tc.timecode_output('smpte'))   # '01:00:00:00'
   print(tc.timecode_output('srt'))     # '01:00:00,000'
   print(tc.timecode_output('ffmpeg'))  # '01:00:00.00'
   print(tc.timecode_output('fcpx'))    # '86400/24s'

   # Get specific parts (1=hours, 2=minutes, 3=seconds, 4=frames/ms)
   print(tc.timecode_output('smpte', output_part=1))  # '01'
   print(tc.timecode_output('smpte', output_part=4))  # '00'

Arithmetic Operations
---------------------

Adding Timecodes
~~~~~~~~~~~~~~~~

.. code-block:: python

   tc1 = DfttTimecode('01:00:00:00', 'auto', fps=24)
   tc2 = DfttTimecode('00:30:00:00', 'auto', fps=24)

   result = tc1 + tc2
   print(result.timecode_output('smpte'))  # '01:30:00:00'

   # Add frames
   result = tc1 + 100
   print(result.timecode_output('smpte'))  # '01:00:04:04'

   # Add seconds
   result = tc1 + 60.0
   print(result.timecode_output('smpte'))  # '01:01:00:00'

Subtracting Timecodes
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   tc1 = DfttTimecode('01:00:00:00', 'auto', fps=24)
   tc2 = DfttTimecode('00:30:00:00', 'auto', fps=24)

   result = tc1 - tc2
   print(result.timecode_output('smpte'))  # '00:30:00:00'

Multiplying and Dividing
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   tc = DfttTimecode('01:00:00:00', 'auto', fps=24)

   # Multiply
   result = tc * 2
   print(result.timecode_output('smpte'))  # '02:00:00:00'

   # Divide
   result = tc / 2
   print(result.timecode_output('smpte'))  # '00:30:00:00'

Comparison Operations
---------------------

.. code-block:: python

   tc1 = DfttTimecode('01:00:00:00', 'auto', fps=24)
   tc2 = DfttTimecode('00:30:00:00', 'auto', fps=24)

   print(tc1 == tc2)  # False
   print(tc1 != tc2)  # True
   print(tc1 > tc2)   # True
   print(tc1 >= tc2)  # True
   print(tc1 < tc2)   # False
   print(tc1 <= tc2)  # False

Changing Timecode Properties
-----------------------------

Changing Frame Rate
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   tc = DfttTimecode('01:00:00:101', 'auto', fps=120)

   # Change FPS with rounding
   tc.set_fps(24, rounding=True)
   print(tc.timecode_output('smpte'))  # Frame-aligned result

   # Change FPS without rounding (preserves timestamp)
   tc.set_fps(24, rounding=False)
   print(tc.timecode_output('smpte'))  # Exact timestamp conversion

Changing Strict Mode
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   tc = DfttTimecode('25:01:02:05', 'auto', fps=24, strict=False)
   print(tc.timecode_output('smpte'))  # '25:01:02:05'

   tc.set_strict(True)
   print(tc.timecode_output('smpte'))  # '01:01:02:05' (wrapped to 24 hours)

Changing Timecode Type
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   tc = DfttTimecode('01:00:00,123', 'auto', fps=24)
   print(tc.type)  # 'srt'

   tc.set_type('smpte', rounding=True)
   print(tc.type)  # 'smpte'
   print(tc.timecode_output('smpte'))  # Frame-aligned SMPTE timecode

Strict Mode
-----------

Strict mode ensures timecodes stay within a 24-hour range:

.. code-block:: python

   # With strict mode enabled (default)
   tc = DfttTimecode('25:00:00:00', 'auto', fps=24, strict=True)
   print(tc.timecode_output('smpte'))  # '01:00:00:00'

   # With strict mode disabled
   tc = DfttTimecode('25:00:00:00', 'auto', fps=24, strict=False)
   print(tc.timecode_output('smpte'))  # '25:00:00:00'

   # Negative values
   tc = DfttTimecode('-01:00:00:00', 'auto', fps=24, strict=True)
   print(tc.timecode_output('smpte'))  # '23:00:00:00'

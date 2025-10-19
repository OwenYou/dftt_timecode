User Guide
==========

This comprehensive guide covers all aspects of using dftt_timecode.

Overview
--------

dftt_timecode is a comprehensive Python library designed for the film and TV industry to handle timecodes
in various formats with high precision. It supports high frame rates (HFR) up to 999.99 fps and provides
a rich set of operations for timecode manipulation.

Key Concepts
------------

Timecode Types
~~~~~~~~~~~~~~

The library supports multiple timecode formats used in different contexts:

- **SMPTE**: Industry-standard format (HH:MM:SS:FF)
- **SRT**: SubRip subtitle format (HH:MM:SS,mmm)
- **FFMPEG**: FFmpeg timestamp format (HH:MM:SS.ff)
- **FCPX**: Final Cut Pro X format (frames/fps)
- **DLP**: Digital cinema format (HH:MM:SS:FFF)
- **Frame**: Simple frame count
- **Time**: Seconds-based timestamp

Frame Rates
~~~~~~~~~~~

The library supports:

- Standard frame rates (23.976, 24, 25, 29.97, 30, 50, 59.94, 60, etc.)
- High frame rates (96, 100, 120, 144, 240, etc.)
- Custom frame rates from 0.01 to 999.99 fps
- Precise fractional frame rates using Python's Fraction type

Drop-Frame vs Non-Drop-Frame
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For NTSC video standards (29.97 fps, 59.94 fps), the library correctly handles:

- Non-drop-frame (NDF): Uses colon separator (HH:MM:SS:FF)
- Drop-frame (DF): Uses semicolon separator (HH:MM:SS;FF)

Drop-frame timecode compensates for the slight discrepancy between nominal and actual frame rates
by periodically skipping frame numbers.

Strict Mode
~~~~~~~~~~~

Strict mode ensures timecodes remain within a 24-hour cycle:

- Enabled: Timecodes wrap around at 24 hours (25:00:00:00 becomes 01:00:00:00)
- Disabled: Timecodes can exceed 24 hours (useful for long-form content)

Common Use Cases
----------------

Video Editing
~~~~~~~~~~~~~

.. code-block:: python

   from dftt_timecode import DfttTimecode

   # Define edit points
   in_point = DfttTimecode('01:05:23:12', 'auto', fps=23.976)
   out_point = DfttTimecode('01:08:45:18', 'auto', fps=23.976)

   # Calculate duration
   duration = out_point - in_point
   print(f"Clip duration: {duration.timecode_output('smpte')}")

Subtitle Timing
~~~~~~~~~~~~~~~

.. code-block:: python

   # SRT format for subtitles
   start = DfttTimecode('00:01:23,456', 'auto', fps=25)
   end = DfttTimecode('00:01:27,890', 'auto', fps=25)

   # Convert to SMPTE for editing
   print(f"Start: {start.timecode_output('smpte')}")
   print(f"End: {end.timecode_output('smpte')}")

Frame Rate Conversion
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Convert from 24fps to 30fps
   tc_24 = DfttTimecode('01:00:00:00', 'auto', fps=24)
   tc_24.set_fps(30, rounding=True)
   print(tc_24.timecode_output('smpte'))

High Frame Rate Workflows
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Working with high frame rate content
   hfr_tc = DfttTimecode('00:10:00:000', 'auto', fps=120)

   # Convert to standard frame rate for delivery
   hfr_tc.set_fps(24, rounding=True)
   print(hfr_tc.timecode_output('smpte'))

Best Practices
--------------

1. **Use Strict Mode for Standard Workflows**: Enable strict mode for typical video editing to prevent
   timecode values from exceeding 24 hours.

2. **Specify Frame Rates Explicitly**: Always specify the correct frame rate when creating timecode
   objects to ensure accurate conversions.

3. **Use Fraction for Precise Frame Rates**: For frame rates like 23.976 or 29.97, use Fraction
   for maximum precision:

   .. code-block:: python

      from fractions import Fraction
      fps = Fraction(24000, 1001)  # Exactly 23.976023976...

4. **Handle Drop-Frame Correctly**: When working with NTSC frame rates (29.97, 59.94), ensure
   drop-frame is set correctly based on your workflow requirements.

5. **Validate User Input**: Use try-except blocks to catch and handle timecode errors gracefully:

   .. code-block:: python

      from dftt_timecode.error import DfttTimecodeError

      try:
          tc = DfttTimecode(user_input, 'auto', fps=24)
      except DfttTimecodeError as e:
          print(f"Invalid timecode: {e}")

Performance Considerations
--------------------------

The library uses high-precision Fraction internally for timestamp storage, which ensures
accuracy but may be slower than floating-point arithmetic. For performance-critical applications:

- Create timecode objects once and reuse them
- Use frame count operations when possible (integer arithmetic is faster)
- Consider caching converted values if the same conversions are needed repeatedly

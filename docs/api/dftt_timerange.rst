DfttTimeRange API
=================

.. currentmodule:: dftt_timecode

.. autoclass:: DfttTimeRange
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __str__, __repr__, __contains__, __eq__, __ne__

Core Class
----------

The :class:`DfttTimeRange` class represents a time range with start and end points, built on top of :class:`DfttTimecode`.

Examples
--------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from dftt_timecode import DfttTimecode, DfttTimeRange

   # Create time range
   start = DfttTimecode('01:00:00:00', 'auto', fps=24)
   end = DfttTimecode('02:00:00:00', 'auto', fps=24)
   range1 = DfttTimeRange(start, end)

   # Get duration
   print(range1.duration.timecode_output('smpte'))  # '01:00:00:00'

Checking Containment and Intersection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   tc = DfttTimecode('01:30:00:00', 'auto', fps=24)

   # Check if timecode is within range
   if tc in range1:
       print("Timecode is within range")

   # Create another range
   range2 = DfttTimeRange(
       DfttTimecode('01:30:00:00', 'auto', fps=24),
       DfttTimecode('02:30:00:00', 'auto', fps=24)
   )

   # Get intersection of two ranges
   intersection = range1.intersect(range2)
   print(intersection)

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

Constructor
~~~~~~~~~~~

.. automethod:: DfttTimeRange.__init__

Properties
~~~~~~~~~~

.. autoproperty:: DfttTimeRange.start
.. autoproperty:: DfttTimeRange.end
.. autoproperty:: DfttTimeRange.duration

Methods
~~~~~~~

.. automethod:: DfttTimeRange.contains
.. automethod:: DfttTimeRange.overlaps
.. automethod:: DfttTimeRange.intersect

Operators
~~~~~~~~~

.. automethod:: DfttTimeRange.__contains__
.. automethod:: DfttTimeRange.__eq__
.. automethod:: DfttTimeRange.__ne__
.. automethod:: DfttTimeRange.__str__
.. automethod:: DfttTimeRange.__repr__

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

Checking Containment
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   tc = DfttTimecode('01:30:00:00', 'auto', fps=24)

   # Check if timecode is within range
   if tc in range1:
       print("Timecode is within range")

Checking Overlaps
~~~~~~~~~~~~~~~~~

.. code-block:: python

   range2 = DfttTimeRange(
       DfttTimecode('01:30:00:00', 'auto', fps=24),
       DfttTimecode('02:30:00:00', 'auto', fps=24)
   )

   # Check if ranges overlap
   if range1.overlaps(range2):
       print("Ranges overlap")

       # Get intersection
       intersection = range1.intersect(range2)
       print(intersection)

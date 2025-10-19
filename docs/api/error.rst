Error Handling
==============

.. currentmodule:: dftt_timecode.error

Exception Classes
-----------------

The dftt_timecode library defines custom exception classes for different error conditions.

DfttTimecodeError
~~~~~~~~~~~~~~~~~

.. autoclass:: DfttTimecodeError
   :members:
   :show-inheritance:

Base exception class for all dftt_timecode errors.

DfttTimecodeValueError
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DfttTimecodeValueError
   :members:
   :show-inheritance:

Raised when an invalid timecode value is provided.

DfttTimecodeTypeError
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DfttTimecodeTypeError
   :members:
   :show-inheritance:

Raised when an invalid timecode type is specified or type mismatch occurs.

DfttTimecodeFPSError
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DfttTimecodeFPSError
   :members:
   :show-inheritance:

Raised when an invalid frame rate is provided.

DfttTimecodeDropFrameError
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DfttTimecodeDropFrameError
   :members:
   :show-inheritance:

Raised when there's an issue with drop-frame timecode handling.

Error Examples
--------------

Invalid Timecode Value
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from dftt_timecode import DfttTimecode
   from dftt_timecode.error import DfttTimecodeValueError

   try:
       tc = DfttTimecode('99:99:99:99', 'smpte', fps=24)
   except DfttTimecodeValueError as e:
       print(f"Invalid timecode: {e}")

Invalid Frame Rate
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from dftt_timecode import DfttTimecode
   from dftt_timecode.error import DfttTimecodeFPSError

   try:
       tc = DfttTimecode('01:00:00:00', 'auto', fps=-24)
   except DfttTimecodeFPSError as e:
       print(f"Invalid FPS: {e}")

Drop-Frame Error
~~~~~~~~~~~~~~~~

.. code-block:: python

   from dftt_timecode import DfttTimecode
   from dftt_timecode.error import DfttTimecodeDropFrameError

   try:
       # Invalid drop-frame timecode (frames 00 and 01 should be dropped at minute boundaries)
       tc = DfttTimecode('00:01:00:00', 'smpte', fps=29.97, drop_frame=True)
   except DfttTimecodeDropFrameError as e:
       print(f"Drop-frame error: {e}")

Type Mismatch
~~~~~~~~~~~~~

.. code-block:: python

   from dftt_timecode import DfttTimecode
   from dftt_timecode.error import DfttTimecodeTypeError

   try:
       tc1 = DfttTimecode('01:00:00:00', 'auto', fps=24)
       tc2 = DfttTimecode('01:00:00:00', 'auto', fps=30)
       # Cannot add timecodes with different frame rates
       result = tc1 + tc2
   except DfttTimecodeTypeError as e:
       print(f"Type error: {e}")

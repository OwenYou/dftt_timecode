Error Handling
==============

.. currentmodule:: dftt_timecode.error

Exception Classes
-----------------

The dftt_timecode library defines custom exception classes for different error conditions.

DFTTError
~~~~~~~~~

.. autoclass:: DFTTError
   :members:
   :show-inheritance:

Base exception class for all dftt_timecode errors.

DFTTTimecodeValueError
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DFTTTimecodeValueError
   :members:
   :show-inheritance:

Raised when an invalid timecode value is provided.

DFTTTimecodeInitializationError
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DFTTTimecodeInitializationError
   :members:
   :show-inheritance:

Raised when timecode initialization fails due to incompatible parameters.

DFTTTimecodeTypeError
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DFTTTimecodeTypeError
   :members:
   :show-inheritance:

Raised when an invalid timecode type is specified or type mismatch occurs.

DFTTTimecodeOperatorError
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DFTTTimecodeOperatorError
   :members:
   :show-inheritance:

Raised when an arithmetic or comparison operation on timecode objects fails.

DFTTTimeRangeMethodError
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DFTTTimeRangeMethodError
   :members:
   :show-inheritance:

Raised when a timerange method is called with invalid parameters or conditions.

DFTTTimeRangeValueError
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DFTTTimeRangeValueError
   :members:
   :show-inheritance:

Raised when a timerange value is invalid or out of acceptable range.

DFTTTimeRangeTypeError
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DFTTTimeRangeTypeError
   :members:
   :show-inheritance:

Raised when a timerange type or operand type is invalid.

DFTTTimeRangeFPSError
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: DFTTTimeRangeFPSError
   :members:
   :show-inheritance:

Raised when timerange operations fail due to frame rate mismatches.

Error Examples
--------------

Invalid Timecode Value
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from dftt_timecode import DfttTimecode
   from dftt_timecode.error import DFTTTimecodeValueError

   try:
       tc = DfttTimecode('99:99:99:99', 'smpte', fps=24)
   except DFTTTimecodeValueError as e:
       print(f"Invalid timecode: {e}")

Timecode Initialization Error
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from dftt_timecode import DfttTimecode
   from dftt_timecode.error import DFTTTimecodeInitializationError

   try:
       # Drop-frame status mismatch with timecode format
       tc = DfttTimecode('01:00:00:00', 'smpte', fps=29.97, drop_frame=False)
   except DFTTTimecodeInitializationError as e:
       print(f"Initialization error: {e}")

Type Error
~~~~~~~~~~

.. code-block:: python

   from dftt_timecode import DfttTimecode
   from dftt_timecode.error import DFTTTimecodeTypeError

   try:
       tc = DfttTimecode('invalid_format', 'unknown_type', fps=24)
   except DFTTTimecodeTypeError as e:
       print(f"Type error: {e}")

Operator Error
~~~~~~~~~~~~~~

.. code-block:: python

   from dftt_timecode import DfttTimecode
   from dftt_timecode.error import DFTTTimecodeOperatorError

   try:
       tc1 = DfttTimecode('01:00:00:00', 'auto', fps=24)
       tc2 = DfttTimecode('01:00:00:00', 'auto', fps=30)
       # Cannot add timecodes with different frame rates
       result = tc1 + tc2
   except DFTTTimecodeOperatorError as e:
       print(f"Operator error: {e}")

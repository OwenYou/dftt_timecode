# Change Log
## V0.0.9
First Public Release.

## V0.0.10

添加 Add:

- 使用DfttTimecode对象初始化新DfttTimecode对象

  Using a DfttTimecode object to instance a new DfttTimecode object.

- DfttTimecode类的float和int方法

  class method float() and int() for DfttTimecode class
  
- DfttTimecode类的precise_timestamp属性

  attribute precise_timestamp for class DfttTimecode

修改 Modify：

- DfttTimecode运算符在未定义/非法操作时将会报错

  Will raise an error when DfttTimecode operators meet undefined circumstances or illegal operations.

- DfttTimecode运算符的大小比较规则

  Compare functions of DfttTimecode operators.
  
- 使用SMPTE NDF格式字符串新建时码类对象时，若强制drop_frame为True，则新建得到的对象为SMPTE DF格式时码

## V0.0.11
添加 Add:
- `__str__`方法,返回DfttTimecode对象的时间码值
  
  `__str__`method,return timecode value for DfttTimecode object

- DfttTimecode单元测试(使用pytest)

  Unit test for DfttTimecode (Using pytest)

修改 Modify：
- 对丢帧的检测条件添加有关23.98/23.976的判定
  
  Add 23.98/23.976FPS to drop frame conditions

- `+` `-`运算符对相加的两个DfttTimecode对象的strict属性进行或运算
  
  `+` `-`operators performs an or operation on the strict property of two DfttTimecode objects that are added together 

- 比较运算符,比如`==` `>` `>=`等,在对两个DfttTimecode对象进行比较的时候会先对两个对象的帧率进行判定,若帧率不同抛出异常
  
  Comparison operators, such as `==`, `>`, `>=`, in the comparison of two DfttTimecode objects will first compare the frame rate of the two objects, if the frame rate is different throw an exception

- `print(self)` 将会输出基于类型的时间码字符串
  
  `print(self)` will output a timecode string

修复 BugFix:
- `timecode_output(self, dest_type, output_part)` 中`output_part = 3`时错误返回分钟数据的问题

  Addressed a problem when `output_part = 3` in `timecode_output(self, dest_type, output_part)` would return minute value in timecode value
  
 ## V0.0.12
 修复 BugFix:
- 修复DLP正则表达式错误导致范围在50-99 150-199的DLP tick不能被匹配的问题。
  这一bug会导致使用形如`'00:00:27:183'`的字符串初始化dlp时间码对象时的报错。

  Fix DLP pattern error causing DLP ticks range [50-99] [150-199] cannot be matched.
  This bug will cause error when using strings like `'00:00:27:183'` to initilize a dlp timecode object.
 
  
V0.0.13 changelog   
## V0.0.13
重构 Refactor:
- 使用`f-string`处理字符串格式输出
  
  Handling string format output using `f-string`

- 重构时间码输出函数,减少代码重复

  Refactor the time code output function to reduce code duplication

添加 Add:
- 添加`get_audio_sample_count` 方法用于正确输出TC时间戳下的音频采样数, 解决issue [#9](https://github.com/OwenYou/dftt_timecode/issues/9)

  Add `get_audio_sample_count` method for correctly outputting the count of audio samples at TC timestamps,solve issue [#9](https://github.com/OwenYou/dftt_timecode/issues/9)

弃用 Deprecate:
- 使用`functools.singledispatchmethod` 代替 `dispatch.InstanceMethodDispatch`

  Use`functools.singledispatchmethod` instead of `dispatch.InstanceMethodDispatch`
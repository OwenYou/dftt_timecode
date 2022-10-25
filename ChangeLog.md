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

  

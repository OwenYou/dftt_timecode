# dftt_timecode

[![pypi](https://img.shields.io/badge/pypi-0.0.9-brightgreen)](https://pypi.org/project/dftt-timecode/)
[![python](https://img.shields.io/badge/python-3-blue)]()
[![GitHub license](https://img.shields.io/badge/license-LGPL2.1-green)](https://github.com/OwenYou/dftt_timecode/blob/main/LICENSE)


## 1. 简介 Introduction

为影视行业设计的Python时码库，支持HFR高帧率以及其他丰富的功能。

Python timecode library for film and TV industry supports HFR and a bunch of cool features.

DFTT是Department of Film and TV Technology of Beijing Film Academy的简称。

DFTT stands for the short of Department of Film and Tv Technology of Beijing Film Academy.

### 1.1 主要功能 Main Features

- 支持多种时码格式输入，如SMPTE、SRT、DLP（Cine Canvas）、FFMPEG、FCPX、帧号、现实时间等。

  Multiple timecode format support, including SMPTE, SRT, DLP(Cine Canvas), FFMPEG, FCPX, frame count, time, etc.

- 支持高帧率，目前支持0.01-999.99fps范围内的帧率。

  High frame rate support, currently supports frame range from 0.01 to 999.99fps.

- 支持严格的丢帧/非丢帧SMPTE格式。

  Strictly support SMPTE DF/NDF format.

- 目前支持-99到99小时时间范围。

  Currently support time range from -99 to 99 hours.

- 支持**严格**模式，在该模式下时码会在0-24小时范围内循环，任意超出该范围的时码会自动转换至范围内。

  **Strict** Mode support, the timecode will circulate from 0 to 24 hours, any timecode outside this range will be automatically converted to a timecode inside it.

- 内部以高精度时间戳进行存储和计算，各类FPS转换、时码格式转换输出都能保持最高精度。

  Uses high precision timestamp inside for storage and calculation, any FPS conversion or format conversion output can maintain their highest precision.

- 常用运算符支持，包括时码与时码、时码与数字的各类加减乘除、比较运算。

  Common operator support, including addition, subtraction, multiplication, division, and comparison operator between two timecode objects or a timecode object and a number.

## 2. 如何安装 How to install

```python
python pip install dftt_timecode
```

### 2.1 包依赖 Package dependency

- fractions
- logging
- math
- functools
- re

## 3. 使用方法说明 How to use 

### 3.1 导入 Import

```python
from dftt_timecode import DfttTimecode
```

### 3.2 新建时码类对象 Create timecode objects

```Python
a = DfttTimecode('01:00:00:00', 'auto', fps=24, drop_frame=False, strict=True)
#以SMPTE非丢帧时码新建对象 Create object using SMPTE NDF
a = DfttTimecode('1000f', 'auto', fps=119.88, drop_frame=True, strict=True)
#以帧数新建对象 Create object using frame count
a = DfttTimecode('3600.0s', 'auto', fps=Fraction(60000,1001), drop_frame=True, strict=True)
#以时间秒新建对象 Create object using time
a = DfttTimecode(-1200, 'auto', fps=23.976, drop_frame=False, strict=False)
#以int帧数新建对象 Create object using int frame count
```

对DfttTimecode()相关参数的详细说明，请查阅`4.1 DfttTimecode()参数说明`。

For detailed parameters descriptions of DfttTimecode(), please refer to chapter `4.1 Parameters Descriptions of DfttTimecode()`.

### 3.3 操作时码类对象 Operate DfttTimecode objects

```python
a = DfttTimecode('01:00:00:00', 'auto', fps=24, drop_frame=False, strict=True)
assert a.type == 'smpte'
assert a.fps == 24
assert a.framecount == 86400
assert a.timestamp == 3600.0
assert a.is_drop_frame == False
assert a.is_strict == True
assert a.timecode_output('smpte',output_part=0) == '01:00:00:00'
assert a.timecode_output('srt',output_part=1) == '01'

a = DfttTimecode('25:00:01:103', 'auto', fps=120, drop_frame=False, strict=False)
a.set_fps(24)
assert a.fps == 24
assert a.timecode_output('smpte') == '25:00:01:21'
a.set_strict(strict=True)
assert a.timecode_output('smpte') == '01:00:01:21'
a.set_strict(strict=False)
assert a.is_strict == False
```
对时码类对象操作的详细说明，请查阅`4.2 时码类对象操作说明`。

For detailed descriptions of DfttTimecode objects' operations, please refer to chapter `4.2 Descriptions of DfttTimecode class operations`.

### 3.4 时码类运算符 Operators of DfttTimecode class

```python
a = DfttTimecode('01:00:00:00', 'auto', fps=24, drop_frame=False, strict=True)
b = DfttTimecode('01:12:34:12', 'auto', fps=24, drop_frame=False, strict=True)
print(a)  # <DfttTimecode>(Timecode:01:00:00:00, Type:smpte, FPS:24.00 NDF, Strict)
print(-a)  # <DfttTimecode>(Timecode:23:00:00:00, Type:smpte, FPS:24.00 NDF, Strict)
print(a + b)  # <DfttTimecode>(Timecode:02:12:34:12, Type:smpte, FPS:24.00 NDF, Strict)
print(a - b)  # <DfttTimecode>(Timecode:23:47:25:12, Type:smpte, FPS:24.00 NDF, Strict)
print(a * 2)  # <DfttTimecode>(Timecode:02:00:00:00, Type:smpte, FPS:24.00 NDF, Strict)
print(a / 2)  # <DfttTimecode>(Timecode:00:30:00:00, Type:smpte, FPS:24.00 NDF, Strict)
print(a == b)  # False
print(a != b)  # True
print(a > b)  # False
print(a >= b)  # False
print(a < b)  # True
print(a <= b)  # True
```

对时码类运算符的详细说明，请查阅`4.3 时码类运算符说明`

For detailed descriptions of DfttTimecode's operators, please refer to chapter `4.3 Descriptions of DfttTimecode class operators`.

## 4 参数详细说明 Detailed Parameters Descriptions

### 4.1 DfttTimecode()参数说明 Parameters Descriptions of DfttTimecode()

#### 4.1.1 参数一览 General Descriptions

```python
a = DfttTimecode(timecode_value, timecode_type, fps, drop_frame, strict)
```

- **`timecode_value`** 是时码对象的时码值，可以是`str`、`int`、`float`、`tuple`、`list`、`Fraction`类型。

  **`timecode_value`** is the value of a timecode, it can be a `str`, `int`, `float`, `tuple`, `list,` or a `Fraction`.

- **`timecode_type`** 是时码对象的类型，是`str`类型，目前支持的时码类型包括`auto`、 `smpte`、 `srt`、 `ffmpeg`、 `fcpx`、 `frame`、 `time`。

  **`timecode_type`** must be a `str`, currently supported timecode types include `auto`, `smpte`, `srt`, `ffmpeg`, `fcpx`, `frame`, `time`.

- **`fps`** 是时码对象的帧率，可以是`int`、`float`、`Fraction`类型。

  **`fps`** is the frame rate of the timecode object, can be an `int`, `float`, or a `Fraction`.

- **`drop_frame`** 是时码对象的丢帧设置，是`bool`类型，只有当帧率存在丢帧格式时，这一设置才会生效，否则会强制将丢帧设为`False`。**`drop_frame `** 的默认值是`False`。

  **`drop_frame`** must be a `bool`, a timecode object can only be drop-frameable under specific frame rate settings, if not so, **`drop_frame`** will be forced to `False`. The default value of **`drop_frame`** is `False`.

- **`strict`** 为时码对象设置严格模式，是`bool`类型。设为`True`后，负值和超过24小时的时码都将被转换为0-24小时范围内的值，例如`25:00:00:00`将被转换为`01:00:00:00`, `-01:00:00:00`将被转换为`23:00:00:00`。 **`strict`** 的默认值是`True`。

  **`strict`** will set the strict mode for a timecode object, it must be a `bool`. When set to `True`, negative timecode value and timecode value over 24 hours will be converted to a value inside the range 0 to 24 hours. For example, 25:00:00:00 will be converted to 01:00:00:00, -01:00:00:00 will be converted to 23:00:00:00. The default value of **`strict`** is `True`.
#### 4.1.2 timecode_value

**`timecode_value`** 决定了时码对象的时间值，DfttTimecode支持以多种类型的数据初始化时间值，且都支持负数。下面详细列出了各个数据类型对应的（可选）初始化方式：

**`timecode_value`** determines the actual time of a timecode object. DfttTimecode supports initialize time by different data types, including negative numbers. The following table lists different data types and their supported initialization methods.

| 数据类型<br />Data type |  支持的初始化方式<br />Supported initialization methods   |
| :---------------------: | :-------------------------------------------------------: |
|          `str`          | `auto`, `smpte`, `srt`, `ffmpeg`, `fcpx`, `frame`, `time` |
|          `int`          |                  `auto`, `frame`, `time`                  |
|         `float`         |                      `auto`, `time`                       |
|         `tuple`         |                      `auto`, `time`                       |
|         `list`          |                      `auto`, `time`                       |
|       `fraction`        |                      `auto`, `time`                       |

目前，DfttTimecode不支持以小数为单位的帧计数方式。

Currently, DfttTimecode does not support frame count value in decimals.

#### 4.1.3 timecode_type

**`timecode_type`** 决定了时码对象的类型。DfttTimecode支持自动判断类型，也支持手动指定类型。在部分场景，如输入值是`int`类时，手动指定类型可以有效地区分以帧计数初始化时码和以时间初始化时码这两种行为。

**`timecode_type`** determines the timecode type of a timecode object. DfttTimecode supports auto-configure timecode type as well as manual assign a timecode type. Under some circumstances, for example, the input data is `int`, manual assign a timecode type is a sufficient way to clarify whether the input is intended to be a frame or a time value.

下表列出了一系列样例**`timecode_value`** 输入和他们在`'auto'`模式下对应的时码类型：

The following sheet gives a list of example **`timecode_value`** input and their corresponding timecode type under `'auto'` mode.

|          timecode_value           | auto模式下的type<br />Type under auto mode |                      备注<br />Comment                       |
| :-------------------------------: | :----------------------------------------: | :----------------------------------------------------------: |
|          `'01:00:00:00'`          |                  `smpte`                   | **`drop_frame`** 将自动设为`False `<br />**`drop_frame`** will be set to `False` |
| `'01:00:00;00'`, `'01:00:00;000'` |                  `smpte`                   | **`drop_frame`** 将自动设为`True`<br />**`drop_frame`** will be set to `True` |
|         `'01:00:00:000'`          |                  `smpte`                   | 高帧率`smpte`时码，形式与`dlp`相近，如果输入值为`dlp`请强制指认**`timecode_type`** 为`dlp`<br />High frame rate timecode, this format is similar to `dlp` timecode, so if your input timecode is actually in `dlp` format, please force **`timecode_type`** to `dlp` |
|         `'01:00:00,000'`          |                   `srt`                    | 最后三位表示毫秒<br />The last three digits represent milliseconds |
|          `'01:00:00.00'`          |                  `ffmpeg`                  | 最后两位表示秒的小数部分<br />The last two digits represent the decimal part of a second |
|        `'1/24s'`, `'1/24'`        |                   `fcpx`                   |             可以省略“s”<br />*s* can be omitted              |
|        `'1000f`, `'1000'`         |                  `frame`                   |             可以省略“f”<br />*f* can be omitted              |
| `’1000s'`,`'1000.0'`,`'1000.0s'`  |                   `time`                   |             可以省略“s”<br />*s* can be omitted              |
|              `1000`               |                  `frame`                   | `int` 数据会自动被认定为`frame`类<br />`int` data will be considered as a `frame` type |
|             `1000.0`              |                   `time`                   | `float` 数据会自动被认定为`time`类<br />`float` data will be considered as a `time` type |
|          `[1000, 2000]`           |                   `time`                   | 前者会成为`Fraction`的分子，后者成为分母<br />the former part will become the numerator of a `Fraction`, and the latter will become the dominator |
|          `(1000, 2000)`           |                   `time`                   | 前者会成为`Fraction`的分子，后者成为分母<br />the former part will become the numerator of a `Fraction`, and the latter will become the dominator |
|      `Fraction(1000, 2000)`       |                   `time`                   | 也可以直接传入一个`Fraction`对象<br />Just passing a `Fraction` object is also acceptable |

如果输入的时码值与所选择的时码类型不匹配，会抛出错误。

If the input timecode value does not match the given timecode type, an error will be raised.

#### 4.1.4 fps

**`fps`** 是时码对象的帧率，可以是`int`、`float`、`Fraction`类型。

**`fps`** is the frame rate of the timecode object, can be an `int`, `float` or a `Fraction`.

#### 4.1.5 drop_frame

**`drop_frame`** 是时码对象的丢帧设置，是`bool`类型，只有当帧率存在丢帧格式时，这一设置才会生效，否则会强制将丢帧设为`False`。**`drop_frame `** 的默认值是`False`。

**`drop_frame`** must be a `bool`, a timecode object can only be drop-frameable under specific frame rate settings, if not so, **`drop_frame`** will be forced to `False`. The default value of **`drop_frame`** is `False`.

当**`timecode_type`** 为`auto`时，会根据输入数据的分隔符自动设置**`drop_frame`** 。

When  **`timecode_type`** is set to `auto`, **`drop_frame`** will be auto-set according to the separator of the input data.

当**`timecode_value`** 在当前**`drop_frame`** 设置下不合法时（仅当**`timecode_type`** 为`smpte`时会有这种情况），将会报错。

When **`timecode_value`** is illegal under the current **`drop_frame`** setting (this should only happen when **`timecode_type`** is `smpte`), there will be an error.

#### 4.1.6 strict

**`strict`** 为时码对象设置严格模式，是`bool`类型。设为`True`后，负值和超过24小时的时码都将被转换为0-24小时范围内的值，例如`25:00:00:00`将被转换为`01:00:00:00`, `-01:00:00:00`将被转换为`23:00:00:00`。**`strict`** 的默认值是`True`。

**`strict`** will set the strict mode for a timecode object, it must be a `bool`. When set to `True`, negative timecode value and timecode value over 24 hours will be converted to a value inside the range 0 to 24 hours. For example, 25:00:00:00 will be converted to 01:00:00:00, -01:00:00:00 will be converted to 23:00:00:00.The default value of **`strict`** is `True`.

特别地，对于丢帧时码，由于严格模式的规则是不出现超过24:00:00:00的时码（实际上这个值会被转为00:00:00:00）。因此，在该模式下可容纳的总帧数会小于相同帧率的非丢帧时码。

In particular, as for a drop-frame timecode, the rule of strict mode does not allow a timecode value greater than 24:00:00:00 (actually, this value will be converted to 00:00:00:00). So, the maximum frame count number a drop-frame timecode can reach under strict mode will be less than a timecode with the same framerate but set to non-drop-frame mode.

#### 4.1.7 补充说明 Additional info

暂无。

Currently, this part intentionally remains blank.

### 4.2 时码类对象操作说明 Descriptions of DfttTimecode class operations

#### 4.2.1 self.type

```python
a = DfttTimecode('01:00:00:00', 'auto', fps=24, drop_frame=False, strict=True)
assert a.type == 'smpte'
```

返回DfttTimecode对象的**`timecode_type`** 属性，返回类型为`str`。

Returns the **`timecode_type`** attribute of a DfttTimecode object, returned data type is `str`.

#### 4.2.2 self.fps

```python
a = DfttTimecode('01:00:00:00', 'auto', fps=24, drop_frame=False, strict=True)
assert a.fps == 24
```

返回DfttTimecode对象的**`fps`** 属性，返回类型取决于设置fps所用的变量类型。

Returns the **`fps`** attribute of a DfttTimecode object, returned data type is determined by the data type used to set the **`fps`** attribute.

#### 4.2.3 self.framecount

```python
a = DfttTimecode('01:00:00:00', 'auto', fps=24, drop_frame=False, strict=True)
assert a.framecount == 86400
```

返回DfttTimecode对象从0时间起经过的总帧数，返回类型为`int`。

Returns the total frame count from 0 of a DfttTimecode, returned data type is `int`.

#### 4.2.4 self.timestamp

```python
a = DfttTimecode('01:00:00:01', 'auto', fps=24, drop_frame=False, strict=True)
assert a.timestamp == 3600.04167
```

返回DfttTimecode对象从0时间起经过的总时长，返回类型为`float`，精度为5位小数。

Returns the total time elapsed from 0 of a DfttTimecode, returned data type is `float`, the precision of the returned value is 5 decimal places.

#### 4.2.5 self.is_drop_frame

```python
a = DfttTimecode('01:00:00:00', 'auto', fps=24, drop_frame=False, strict=True)
assert a.is_drop_frame == False
```

返回DfttTimecode对象的**`drop_frame`** 属性，返回类型为`bool`.

Returns the **`drop_frame`** attribute of a DfttTimecode object, returned data type is `bool`.

#### 4.2.6 self.is_strict

```python
a = DfttTimecode('01:00:00:00', 'auto', fps=24, drop_frame=False, strict=True)
assert a.is_strict == True
```

返回DfttTimecode对象的**`strict`** 属性，返回类型为`bool`.

Returns the **`strict`** attribute of a DfttTimecode object, returned data type is `bool`.

#### 4.2.7 self.set_fps()

```python
a = DfttTimecode('01:00:00:101', 'auto', fps=120, drop_frame=False, strict=True)
a.set_fps(24, rounding = True)
a.set_fps(120)
assert a.timecode_output('smpte') == '01:00:00:100'
```

该函数会更改DfttTimecode对象的帧率，并可以选择在更改帧率时是否取整。

This function will change the frame rate of a DfttTimecode object, you can choose whether or not to round the timecode value while changing the frame rate.

`self.set_fps()`函数共有两个参数，分别是**`dest_fps`** 和**`rounding`**。

There are two parameters of `self.set_fps()`, they are **`dest_fps`** and **`rounding`**.

**`dest_fps`** 是帧率转换的目标帧率，可以是`int`、`float`、`Fraction`类型。

**`dest_fps`** is the target frame rate of this transform, it can be a,n `int`,  `float`, or a `Fraction`.

**`rounding`** 决定了帧率转换过程中是否舍入时间戳以对齐帧，具体可以参考下面的示例代码。

**`rounding`** determines whether to round the time stamp to align to the exact frame while converting the frame rate, you can refer to the following example code to see how it works.

```python
a = DfttTimecode('01:00:00:101', 'auto', fps=120, drop_frame=False, strict=True)
a.set_fps(24, rounding = False)
a.set_fps(120)
assert a.timecode_output('smpte') == '01:00:00:101'
a.set_fps(24, rounding = True)
a.set_fps(120)
assert a.timecode_output('smpte') == '01:00:00:100'
```

#### 4.2.8 self.set_type()

```python
a = DfttTimecode('01:00:00,123', 'auto', fps=24)
a.set_type('smpte', rounding=True)
assert a.type == 'smpte'
a.set_type('srt')
assert a.timecode_output('srt') == '01:00:00,125'
```

该函数会更改DfttTimecode对象的时码类型，并可以选择在更改类型时是否取整。

This function will change the timecode type of a DfttTimecode object, you can choose whether or not to round the timecode value while changing the timecode type.

`self.set_type()`函数共有两个参数，分别是**`dest_type`** 和**`rounding`**。

`self.set_type()` has two parameters, they are **`dest_type`** and **`rounding`**  .

**`dest_type`** 是时码类型转换的目标时码类型，可以是除`'auto'`以外的任何一个支持的时码类型。

**`dest_type`** is the target timecode type of this transform, it can be any supported timecode type except `'auto'`.

**`rounding`** 决定了时码类型转换过程中是否舍入时间戳以对齐帧，具体可以参考下面的示例代码。

**`rounding`** determines whether to round the time stamp to align to the exact frame while converting the timecode type, you can refer to the following example code to see how it works.

```python
a = DfttTimecode('01:00:00,123', 'auto', fps=24)
assert a.type == 'srt'
a.set_type('smpte', rounding=True)
assert a.type == 'smpte'
assert a.timecode_output('srt') == '01:00:00,125'
```

#### 4.2.9 self.set_strict()

```python
a = DfttTimecode('25:01:02:05', 'auto', fps=24, strict=False)
a.set_strict()
assert a.is_strict == True
assert a.timecode_output('smpte') == '01:01:02:05'
a.set_strict(strict=False)
assert a.is_strict == False
```

该函数会更改DfttTimecode对象的strict模式布尔值。

This function will change the strict mode bool value of a DfttTimecode object.

`self.set_strict()` 只有一个参数，即**`strict`** 。**`strict`** 的类型是`bool`，默认值为`True`。

`self.set_strict()` has one parameter, which is **`strict`**. The data type of **`strict`** is `bool`, the default value of **`strict`** is `Ture`. 

#### 4.2.10 self.timecode_output()

```python
a = DfttTimecode('01:02:03:05', 'auto', fps=24)
assert a.timecode_output() == '01:02:03:05'
assert a.timecode_output('srt') == '01:02:03,208'
assert a.timecode_output('srt', output_part=1) == '01'
assert a.timecode_output('srt', output_part=2) == '02'
assert a.timecode_output('srt', output_part=3) == '03'
assert a.timecode_output('srt', output_part=4) == '208'
```

该函数会以指定类型和部分返回DfttTimecode对象的时码值，返回类型为`str`。

This function will return the timecode value of a DfttTimecode object in the given timecode type and partition number format, the returned data type is `str`.

`self.timecode_output()` 有两个参数，分别是**`dest_type`** 和**`output_part`** 。

`self.timecode_output()` has two parameters, they are **`dest_type`** and **`output_part`** .

**`dest_type`** 是输出时码的类型，可以是任何一个支持的时码类型，它的默认值是`'auto'`，此时会根据DfttTimecode对象自身的时码类型决定输出类型。

**`dest_type`** is the type of the output timecode value, it can be any supported timecode type, the default value of it is `'auto'`, which means the function will determine the output timecode type according to the timecode type of the DfttTimecode object itself.

**`output_part`** 是输出的部分，它应是一个`int`值。它的默认值是`0`，即完整输出。`1`到`4`依次代表输出从左至右的每个时码部分。

**`output_part`** is the partition of the output timecode value, it is an `int`. The default value of it is 0, which means a complete output. Each of 1 to 4 represents an output timecode part from left to right.

### 4.3 时码类运算符说明 Descriptions of DfttTimecode class operators

#### 4.3.1 print(self)

该运算符会打印DfttTimecode对象相关的基本信息，如下所示。

This operator will print basic information of a DfttTimecode object, as the following codes show.

```python
a = DfttTimecode('01:00:00,123', 'srt', fps=24, drop_frame=False, strict=True)
print(a)  # <DfttTimecode>(Timecode:01:00:00,123, Type:srt, FPS:24.00 NDF, Strict)
```

#### 4.3.2 -self

该运算符会将DfttTimecode对象的时码值取负，且不改变其他属性，如下所示。

This operator will yield the negation of the timecode value of a DfttTimecode object, and won't affect any of the rest attributes, as the following codes show.

```python
a = DfttTimecode('01:00:00,123', 'srt', fps=24, drop_frame=False, strict=True)
print(-a)  # <DfttTimecode>(Timecode:22:59:59,877, Type:srt, FPS:24.00 NDF, Strict)
```

#### 4.3.3 +

该运算符可以将两个DfttTimecode对象相加，或将DfttTimecode对象与`int`，`float`或`Fraction`相加。

This operator can add two DfttTimecode objects together, or add a DfttTimecode object with an `int`, `float`, or a `Fraction`.

当DfttTimecode对象与`int`相加时，`int`值将被当作帧计数处理。当DfttTimecode对象与`float`或`Fraction`相加时，后者的值将被当作时间戳处理。

When adding a DfttTimecode object with an `int`, the `int` will be considered as a frame number. When adding a DfttTimecode object with a `float` or a `Fraction`, the latter will be considered as a time stamp.

相加的DfttTimecode对象必须拥有相同的帧率。

The two DfttTimecode objects to perform the addition must have the same frame rate.

#### 4.3.4 -

该运算符可以将两个DfttTimecode对象相减，或将DfttTimecode对象与`int`，`float`或`Fraction`相减。

This operator can perform a subtraction between two DfttTimecode objects, or perform a subtraction between a DfttTimecode object and an `int`, `float`, or a `Fraction`.

当DfttTimecode对象与`int`相减时，`int`值将被当作帧计数处理。当DfttTimecode对象与`float`或`Fraction`相加时，后者的值将被当作时间戳处理。

When performing a subtraction between a DfttTimecode object and an `int`, the `int` will be considered as a frame number. When performing a subtraction between a DfttTimecode object and a `float` or a `Fraction`, the latter will be considered as a time stamp.

相减的DfttTimecode对象必须拥有相同的帧率。

The two DfttTimecode objects to perform the subtraction must have the same frame rate.

#### 4.3.5 \*

该运算符可以将一个DfttTimecode对象与一个`int`，`float`或`Fraction`相乘，后者的数学意义是倍数。

This operator can perform a multiplication between a DfttTimecode object and an `int`, `float`, or a `Fraction`, the mathematical meaning of the latter is a factor.

#### 4.3.6 /

该运算符可以将一个DfttTimecode对象与一个`int`，`float`或`Fraction`相除，后者的数学意义是倍数。

This operator can perform a division between a DfttTimecode object and an `int`, `float`, or a `Fraction`, the mathematical meaning of the latter is a factor.

需要注意的是，只有当DfttTimecode对象作为被除数时，除法运算才是有意义的，DfttTimecode对象不能作除数。

Please be noted, the division operation only makes sense when the DfttTimecode object is used as the dividend, the DfttTimecode object cannot be used as a divisor.

#### 4.3.7 ==

该运算符可以比较两个DfttTimecode对象是否相等，或比较DfttTimecode对象和`int`，`float`或`Fraction`是否相等。

This operator can perform a comparison between two DfttTimecode objects, or perform a comparison between a DfttTimecode object and an `int`, `float`, or a `Fraction`, to tell whether they are equal to each other.

当两个DfttTimecode对象作比较时，将比较二者的时间戳。当DfttTimecode对象与`int`作比较时，`int`值将被当作帧计数处理。当DfttTimecode对象与`float`或`Fraction`作比较时，后者的值将被当作时间戳处理。

When performing a comparison between two DfttTimecode objects, a comparison of their timestamp will be performed. When performing a comparison between a DfttTimecode object and an `int`, the `int` will be considered as a frame number. When performing a comparison between a DfttTimecode object and a `float` or a `Fraction`, the latter will be considered as a time stamp.

#### 4.3.8 \!=

该运算符可以比较两个DfttTimecode对象是否相等，或比较DfttTimecode对象和`int`，`float`或`Fraction`是否相等。

This operator can perform a comparison between two DfttTimecode objects, or perform a comparison between a DfttTimecode object and an `int`, `float`, or a `Fraction`, to tell whether they are equal to each other.

当两个DfttTimecode对象作比较时，将比较二者的时间戳。当DfttTimecode对象与`int`作比较时，`int`值将被当作帧计数处理。当DfttTimecode对象与`float`或`Fraction`作比较时，后者的值将被当作时间戳处理。

When performing a comparison between two DfttTimecode objects, a comparison of their timestamp will be performed. When performing a comparison between a DfttTimecode object and an `int`, the `int` will be considered as a frame number. When performing a comparison between a DfttTimecode object and a `float` or a `Fraction`, the latter will be considered as a time stamp.

#### 4.3.9 >

该运算符可以比较两个DfttTimecode对象的大小，或比较DfttTimecode对象和`int`，`float`或`Fraction`的大小。

This operator can perform a comparison between two DfttTimecode objects, or perform a comparison between a DfttTimecode object and an `int`, `float`, or a `Fraction`, to tell which one is the greater one.

当两个DfttTimecode对象作比较时，将比较二者的时间戳。当DfttTimecode对象与`int`作比较时，`int`值将被当作帧计数处理。当DfttTimecode对象与`float`或`Fraction`作比较时，后者的值将被当作时间戳处理。

When performing a comparison between two DfttTimecode objects, a comparison of their timestamp will be performed. When performing a comparison between a DfttTimecode object and an `int`, the `int` will be considered as a frame number. When performing a comparison between a DfttTimecode object and a `float` or a `Fraction`, the latter will be considered as a time stamp.

#### 4.3.10 >=

该运算符可以比较两个DfttTimecode对象的大小，或比较DfttTimecode对象和`int`，`float`或`Fraction`的大小。

This operator can perform a comparison between two DfttTimecode objects, or perform a comparison between a DfttTimecode object and an `int`, `float`, or a `Fraction`, to tell which one is the greater one.

当两个DfttTimecode对象作比较时，将比较二者的时间戳。当DfttTimecode对象与`int`作比较时，`int`值将被当作帧计数处理。当DfttTimecode对象与`float`或`Fraction`作比较时，后者的值将被当作时间戳处理。

When performing a comparison between two DfttTimecode objects, a comparison of their timestamp will be performed. When performing a comparison between a DfttTimecode object and an `int`, the `int` will be considered as a frame number. When performing a comparison between a DfttTimecode object and a `float` or a `Fraction`, the latter will be considered as a time stamp.

#### 4.3.11 <

该运算符可以比较两个DfttTimecode对象的大小，或比较DfttTimecode对象和`int`，`float`或`Fraction`的大小。

This operator can perform a comparison between two DfttTimecode objects, or perform a comparison between a DfttTimecode object and an `int`, `float`, or a `Fraction`, to tell which one is the greater one.

当两个DfttTimecode对象作比较时，将比较二者的时间戳。当DfttTimecode对象与`int`作比较时，`int`值将被当作帧计数处理。当DfttTimecode对象与`float`或`Fraction`作比较时，后者的值将被当作时间戳处理。

When performing a comparison between two DfttTimecode objects, a comparison of their timestamp will be performed. When performing a comparison between a DfttTimecode object and an `int`, the `int` will be considered as a frame number. When performing a comparison between a DfttTimecode object and a `float` or a `Fraction`, the latter will be considered as a time stamp.

#### 4.3.12 <=

该运算符可以比较两个DfttTimecode对象的大小，或比较DfttTimecode对象和`int`，`float`或`Fraction`的大小。

This operator can perform a comparison between two DfttTimecode objects, or perform a comparison between a DfttTimecode object and an `int`, `float`, or a `Fraction`, to tell which one is the greater one.

当两个DfttTimecode对象作比较时，将比较二者的时间戳。当DfttTimecode对象与`int`作比较时，`int`值将被当作帧计数处理。当DfttTimecode对象与`float`或`Fraction`作比较时，后者的值将被当作时间戳处理。

When performing a comparison between two DfttTimecode objects, a comparison of their timestamp will be performed. When performing a comparison between a DfttTimecode object and an `int`, the `int` will be considered as a frame number. When performing a comparison between a DfttTimecode object and a `float` or a `Fraction`, the latter will be considered as a time stamp.


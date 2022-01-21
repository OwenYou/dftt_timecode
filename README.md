# dftt_timecode

[![pypi](https://img.shields.io/badge/pypi-0.0.9-brightgreen)](https://pypi.org/project/dftt-timecode/)
[![python](https://img.shields.io/badge/python-3-blue)]()
[![GitHub license](https://img.shields.io/badge/license-LGPL2.1-green)](https://github.com/OwenYou/dftt_timecode/blob/main/LICENSE)


## 1. 简介 Introduction

为影视行业设计的Python时码库，支持HFR高帧率以及其他丰富的功能。

Python timecode library for film and TV industry, supports HFR and a bunch of cool features.

### 1.1 主要功能 Main Features

- 支持多种时码格式输入，如SMPTE、SRT、DLP（Cine Canvas）、FFMPEG、FCPX、帧号、现实时间等。

  Multiple timecode format support, including SMPTE, SRT, DLP(Cine Canvas), FFMPEG, FCPX, frame count, time, etc.

- 支持高帧率，目前支持0.01-999.99fps范围内的帧率。

  High frame rate support, currently support frame range from 0.01 to 999.99fps.

- 支持严格的丢帧/非丢帧SMPTE格式。

  Strictly support SMPTE DF/NDF format.

- 目前支持-99到99小时时间范围。

  Currently support time range from -99 to 99 hours.

- 支持**严格**模式，在该模式下时码会在0-24小时范围内循环，任意超出该范围的时码会自动转换至范围内。

  **Strict** Mode support, timecode will circulate from 0 to 24 hours, any timecode outside this range will be automaticly converted to a timecode inside it.

- 内部以高精度时间戳进行存储和计算，各类FPS转换、时码格式转换输出都能保持最高精度。

  Uses high precision time stamp inside for storage and calculation, any FPS conversion or format conversion output can maintain their highest precision.

- 常用运算符支持，包括时码与时码、时码与数字的各类加减乘除、比较运算。

  Common operator support, including addtion, subtraction, multiplication, division and comparison operator between two timecode object or a timecode object and a number.

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

对时码类运算符的详细说明，请查阅`4.3 时码类运算符说明`

For detailed descriptions of DfttTimecode's operators, please refer to chapter `4.3 Descriptions of DfttTimecode class operators`.

## 4 参数详细说明 Detailed Parameters Descriptions

### 4.1 DfttTimecode()参数说明 Parameters Descriptions of DfttTimecode()

#### 4.1.1 参数一览 General Descriptions

```python
a = DfttTimecode(timecode_value, timecode_type, fps, drop_frame, strict)
```

- **`timecode_value`** 是时码对象的时码值，可以是`str`、`int`、`float`、`tuple`、`list`、`Fraction`类型。

  **`timecode_value`** is the value of a timecode, it can be a `str`, `int`, `float`, `tuple`, `list` or a `Fraction`.

- **`timecode_type`** 是时码对象的类型，是`str`类型，目前支持的时码类型包括`auto`、 `smpte`、 `srt`、 `ffmpeg`、 `fcpx`、 `frame`、 `time`。

  **`timecode_type`** must be a `str`, currently supported timecode types include `auto`, `smpte`, `srt`, `ffmpeg`, `fcpx`, `frame`, `time`.

- **`fps`** 是时码对象的帧率，可以是`int`、`float`、`Fraction`类型。

  **`fps`** is the frame rate of the timecode object, can be a `int`, `float` or a `Fraction`.

- **`drop_frame`** 是时码对象的丢帧设置，是`bool`类型，只有当帧率存在丢帧格式时，这一设置才会生效，否则会强制将丢帧设为`False`。**`drop_frame `** 的默认值是`False`。

  **`drop_frame`** must be a `bool`, a timecode object can only be drop-frameable under spcific frame rate settings, if not so, **`drop_frame`** will be forced to `False`. The default value of **`drop_frame`** is `False`.

- **`strict`** 为时码对象设置严格模式，是`bool`类型。设为`True`后，负值和超过24小时的时码都将被转换为0-24小时范围内的值，例如`25:00:00:00`将被转换为`01:00:00:00`, `-01:00:00:00`将被转换为`23:00:00:00`。

  **`strict`** will set strict mode for a timecode object, it must be a `bool`. When set to `True`, negative timecode value and timecode value over 24 hours will be converted to a value inside range 0 to 24 hours. For example, 25:00:00:00 will be converted to 01:00:00:00, -01:00:00:00 will be converted to 23:00:00:00.
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

**`timecode_type`** 决定了时码对象的类型，DfttTimecode支持自动判断类型，也支持手动指定类型。在部分场景，如输入值是`int`类时，手动指定类型可以有效地区分以帧计数初始化时码和以时间初始化时码这两种行为。

下表列出了一系列样例timecode_value输入和他们在auto模式下对应的时码类型：

|          timecode_value           | auto模式下的type<br />Type under auto mode |                      备注<br />Comment                       |
| :-------------------------------: | :----------------------------------------: | :----------------------------------------------------------: |
|          `'01:00:00:00'`          |                  `smpte`                   | **`drop_frame`** 将自动设为`False `<br />**`drop_frame`** will be set to `False` |
| `'01:00:00;00'`, `'01:00:00;000'` |                  `smpte`                   | **`drop_frame`** 将自动设为`True`<br />**`drop_frame`** will be set to `True` |
|         `'01:00:00:000'`          |                  `smpte`                   | 高帧率`smpte`时码，形式与`dlp`相近，如果输入值为`dlp`请强制指认**`timecode_type`** 为`dlp`<br />High frame rate timecode, this format is similar to `dlp` timecode, so if your input timecode is actually in `dlp` format, please force **`timecode_type`** to `dlp` |
|         `'01:00:00,000'`          |                   `srt`                    | 最后三位表示毫秒<br />The last three digits represents milliseconds |
|          `'01:00:00.00'`          |                  `ffmpeg`                  | 最后两位表示秒的小数部分<br />The last two digits represents the decimal part of a second |
|        `'1/24s'`, `'1/24'`        |                   `fcpx`                   |             可以省略“s”<br />*s* can be omitted              |
|        `'1000f`, `'1000'`         |                  `frame`                   |             可以省略“f”<br />*f* can be omitted              |
| `’1000s'`,`'1000.0'`,`'1000.0s'`  |                   `time`                   |             可以省略“s”<br />*s* can be omitted              |
|              `1000`               |                  `frame`                   | `int` 数据会自动被认定为`frame`类<br />`int` data will be considered as a `frame` type |
|             `1000.0`              |                   `time`                   | `float` 数据会自动被认定为`time`类<br />`float` data will be considered as a `time` type |
|           [1000, 2000]            |                   `time`                   | 前者会成为`Fraction`的分子，后者成为分母<br />the former part will become the numerator of a `Fraction`, and the latter will become the dominator |
|           (1000, 2000)            |                   `time`                   | 前者会成为`Fraction`的分子，后者成为分母<br />the former part will become the numerator of a `Fraction`, and the latter will become the dominator |
|       Fraction(1000, 2000)        |                   `time`                   | 也可以直接传入一个`Fraction`对象<br />Just pass a `Fration` object is also acceptable |

#### 4.1.4 fps

**`fps`** 是时码对象的帧率，可以是`int`、`float`、`Fraction`类型。

**`fps`** is the frame rate of the timecode object, can be a `int`, `float` or a `Fraction`.

#### 4.1.5 drop_frame

**`drop_frame`** 是时码对象的丢帧设置，是`bool`类型，只有当帧率存在丢帧格式时，这一设置才会生效，否则会强制将丢帧设为`False`。**`drop_frame `** 的默认值是`False`。

**`drop_frame`** must be a `bool`, a timecode object can only be drop-frameable under spcific frame rate settings, if not so, **`drop_frame`** will be forced to `False`. The default value of **`drop_frame`** is `False`.

当**`timecode_type`** 为`auto`时，会根据输入数据的分隔符自动设置**`drop_frame`** 。

When  **`timecode_type`** is set to `auto`, **`drop_frame`** will be auto set according to the separator of the input data.

当**`timecode_value`** 在当前**`drop_frame`** 设置下不合法时（仅当**`timecode_type`** 为`smpte`时会有这种情况），将会报错。

When **`timecode_value`** is illegal under current **`drop_frame`** setting (this should only happend when **`timecode_type`** is `smpte`), there will be an error.

#### 4.1.6 strict

**`strict`** 为时码对象设置严格模式，是`bool`类型。设为`True`后，负值和超过24小时的时码都将被转换为0-24小时范围内的值，例如`25:00:00:00`将被转换为`01:00:00:00`, `-01:00:00:00`将被转换为`23:00:00:00`。

**`strict`** will set strict mode for a timecode object, it must be a `bool`. When set to `True`, negative timecode value and timecode value over 24 hours will be converted to a value inside range 0 to 24 hours. For example, 25:00:00:00 will be converted to 01:00:00:00, -01:00:00:00 will be converted to 23:00:00:00.

特别地，对于丢帧时码，由于严格模式的规则是不出现超过24:00:00:00的时码（实际上这个值会被转为00:00:00:00）。因此，在该模式下可容纳的总帧数会小于相同帧率的非丢帧时码。

In particular, as for a dropframe timecode, because the rule of strict mode do not allow there to be a timecode value greater than 24:00:00:00 (actually this value will be converted to 00:00:00:00). So, under strict mode, the maximum frame count number a dropframe timecode can reach will be less than a timecode with the same framerate but set to non-dropframe mode.

#### 4.1.7 补充说明 Additional info

暂无。

Currently this part is intentionally remained blank.

### 4.2 时码类对象操作说明 Descriptions of DfttTimecode class operations

#### 4.2.1 self.type

#### 4.2.2 self.fps

#### 4.2.3 self.framecount

#### 4.2.4 self.is_drop_frame

#### 4.2.5 self.is_strict

#### 4.2.6 self.set_fps()

#### 4.2.7 self.set_type()

#### 4.2.8 self.set_strict()

### 4.3 时码类运算符说明 Descriptions of DfttTimecode class operators

#### 4.3.1 \_\_repr\_\_()

#### 4.3.2 +

#### 4.3.3 -

#### 4.3.4 \*

#### 4.3.5 /

#### 4.3.6 =

#### 4.3.7 \!=

#### 4.3.8 >

#### 4.3.9 >=

#### 4.3.10 <

#### 4.3.11 <=


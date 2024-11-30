from fractions import Fraction
import pytest
import dftt_timecode.error as dftt_errors
from dftt_timecode import DfttTimecode as TC


@pytest.fixture(
    params=[
        ("00:00:01:00", "auto", 24, False, True),
        ("1000", "auto", 119.88, True, True),
        ("1.0", "auto", Fraction(60000, 1001), True, True),
        ("00:01:00;02", "auto", 29.97, True, True),
        ("01:00:00,123", "auto", 24, False, True),
    ],
    ids=["smpte", "frame", "time", "smpte_df", "srt"],
)
def tc_data(request):
    return request.param


def test_tc_instance(tc_data):
    assert isinstance(TC(*tc_data), TC)


@pytest.mark.parametrize(
    "timecode_value, timecode_type, fps, drop_frame, strict, result_type",
    [
        ("01:00:00:00", "smpte", 24, False, True, "smpte"),
        ("1000f", "frame", 119.88, True, True, "frame"),
        ("3600.0s", "time", Fraction(60000, 1001), True, True, "time"),
    ],
    ids=["smpte", "frame", "time"],
)
def test_type(timecode_value, timecode_type, fps, drop_frame, strict, result_type):
    assert (
        TC(timecode_value, timecode_type, fps, drop_frame, strict).type == result_type
    )


@pytest.mark.parametrize(
    "timecode_value, timecode_type, fps, drop_frame, strict, result_type",
    [
        ("01:00:00:00", "auto", 24, False, True, "smpte"),
        ("1000f", "auto", 119.88, True, True, "frame"),
        ("3600.0s", "auto", Fraction(60000, 1001), True, True, "time"),
    ],
    ids=["smpte", "frame", "time"],
)
def test_auto_type(timecode_value, timecode_type, fps, drop_frame, strict, result_type):
    assert TC(timecode_value, "auto", fps, drop_frame, strict).type == result_type


@pytest.mark.parametrize(
    "timecode_value, timecode_type, fps, drop_frame, strict",
    [
        ("01:00:00:23", "smpte", 20, False, True),
    ],
    ids=["smpte"],
)
def test_invalid_timecode(timecode_value, timecode_type, fps, drop_frame, strict):
    from dftt_timecode.error import DFTTTimecodeValueError

    with pytest.raises(DFTTTimecodeValueError):
        TC(timecode_value, timecode_type, fps, drop_frame, strict)


@pytest.mark.parametrize(
    "timecode_value, timecode_type, fps, drop_frame, strict, result_fps",
    [
        ("01:00:00:00", "auto", 24, False, True, 24),
        ("1000f", "auto", 119.88, True, True, 119.88),
        ("3600.0s", "auto", Fraction(60000, 1001), True, True, Fraction(60000, 1001)),
    ],
    ids=["smpte", "frame", "time"],
)
def test_fps(timecode_value, timecode_type, fps, drop_frame, strict, result_fps):
    assert TC(timecode_value, timecode_type, fps, drop_frame, strict).fps == result_fps


@pytest.mark.parametrize(
    "timecode_value, timecode_type, fps, drop_frame, strict, result_framecount",
    [
        ("00:00:01:00", "auto", 24, False, True, 24),
        ("1000f", "auto", 119.88, True, True, 1000),
        ("1.0s", "auto", Fraction(60000, 1001), True, True, 60),
        ("00:01:00;02", "auto", 29.97, True, True, 1800),
    ],
    ids=["smpte", "frame", "time", "smpte_nf"],
)
def test_framecount(
    timecode_value, timecode_type, fps, drop_frame, strict, result_framecount
):
    assert (
        TC(timecode_value, timecode_type, fps, drop_frame, strict).framecount
        == result_framecount
    )


@pytest.mark.parametrize(
    "timecode_value, timecode_type, fps, drop_frame, strict",
    [
        ("00:00:01:00", "auto", 24, False, True),
        ("1000f", "auto", 119.88, True, True),
        ("1.0s", "auto", Fraction(60000, 1001), True, True),
        ("00:01:00;02", "auto", 29.97, True, True),
    ],
    ids=["smpte", "frame", "time", "smpte_nf"],
)
def test_dropframe_strict(timecode_value, timecode_type, fps, drop_frame, strict):
    assert (
        TC(timecode_value, timecode_type, fps, drop_frame, strict).is_drop_frame
        is drop_frame
    )
    assert (
        TC(timecode_value, timecode_type, fps, drop_frame, strict).is_strict is strict
    )


@pytest.fixture(
    params=[
        ("00:01:01:01", "auto", 24, False, True, 61.04167, Fraction(1465 / 24)),
        ("1000f", "auto", 119.88, True, True, 8.34168, Fraction(1000 / 119.88)),
        ("1.0s", "auto", Fraction(60000 / 1001), True, True, 1, 1),
        ("00:01:00;02", "auto", 29.97, True, True, 60.06006, Fraction(1800 / 29.97)),
    ],
    ids=["smpte", "frame", "time", "smpte_nf"],
)
def timestamp_data(request):
    return request.param


def test_timestamp(timestamp_data):
    assert TC(*timestamp_data[:-2]).timestamp == pytest.approx(timestamp_data[-2])


def test_precise_timestamp(timestamp_data):
    assert TC(*timestamp_data[:-2]).precise_timestamp == timestamp_data[-1]


@pytest.fixture(
    params=[
        ("01:00:00:101", "auto", 120, False, True, 24, True, "01:00:00:100"),
        ("01:00:00:101", "auto", 120, False, True, 24, False, "01:00:00:101"),
    ],
    ids=["120_24_Round", "120_24_NRound"],
)
def set_fps_data(request):
    yield request.param


def test_set_fps(set_fps_data):
    tc = TC(*set_fps_data[:-3])
    tc.set_fps(set_fps_data[-3], rounding=set_fps_data[-2])
    assert tc.fps == set_fps_data[-3]
    tc.set_fps(set_fps_data[2])
    assert tc.timecode_output("smpte") == set_fps_data[-1]


@pytest.fixture(
    params=[
        ("00:00:01:101", "auto", 120, False, True, "frame", True, "221"),
        ("00:00:01,123", "auto", 120, False, True, "smpte", True, "00:00:01:015"),
    ],
    ids=["smpte_frame", "srt_smpte_round"],
)
def set_type_data(request):
    yield request.param


def test_set_type(set_type_data):
    tc = TC(*set_type_data[:-3])
    tc.set_type(set_type_data[-3], rounding=set_type_data[-2])
    assert tc.type == set_type_data[-3]
    assert tc.timecode_output(set_type_data[-3]) == set_type_data[-1]


@pytest.fixture(
    params=[
        ("25:00:01:101", "auto", 120, False, False, True, "01:00:01:101"),
        ("24:00:00:01", "auto", 24, False, False, True, "00:00:00:01"),
    ],
    ids=["120FPS", "24FPS"],
)
def set_strict_data(request):
    yield request.param


def test_set_strict(set_strict_data):
    tc = TC(*set_strict_data[:-2])
    assert tc.is_strict == set_strict_data[-3]
    tc.set_strict()
    assert tc.is_strict == set_strict_data[-2]
    assert tc.timecode_output("smpte") == set_strict_data[-1]


@pytest.mark.parametrize(
    argnames="timecode_value, timecode_type, fps, drop_frame, strict,output_smpte,output_frame,output_time,output_srt,output_fcpx,output_ffmpeg",
    argvalues=[
        (
            "00:00:01:00",
            "auto",
            24,
            False,
            True,
            "00:00:01:00",
            "24",
            "1.0",
            "00:00:01,000",
            "1s",
            "00:00:01.00",
        ),
        (
            "00:10:00;00",
            "auto",
            29.97,
            True,
            True,
            "00:10:00;00",
            "17982",
            "600.0",
            "00:10:00,000",
            "600s",
            "00:10:00.00",
        ),
    ],
    ids=["NDF", "DF"],
)
def test_timecode_output(
    timecode_value,
    timecode_type,
    fps,
    drop_frame,
    strict,
    output_smpte,
    output_frame,
    output_time,
    output_srt,
    output_fcpx,
    output_ffmpeg,
):
    tc = TC(timecode_value, timecode_type, fps, drop_frame, strict)
    assert tc.timecode_output() == timecode_value
    assert tc.timecode_output("smpte") == output_smpte
    assert tc.timecode_output("frame") == output_frame
    assert tc.timecode_output("time") == output_time
    assert tc.timecode_output("srt") == output_srt
    assert tc.timecode_output("fcpx") == output_fcpx
    assert tc.timecode_output("ffmpeg") == output_ffmpeg


@pytest.mark.parametrize(
    argnames="timecode_value, timecode_type, fps, drop_frame, strict,output_type,output_str,part_1,part_2,part_3,part_4",
    argvalues=[
        (
            "11:22:33:13",
            "auto",
            24,
            False,
            True,
            "smpte",
            "11:22:33:13",
            "11",
            "22",
            "33",
            "13",
        ),
        (
            "11:22:33,456",
            "auto",
            24,
            False,
            True,
            "srt",
            "11:22:33,456",
            "11",
            "22",
            "33",
            "456",
        ),
    ],
    ids=["smpte", "srt"],
)
def test_timecode_output_part(
    timecode_value,
    timecode_type,
    fps,
    drop_frame,
    strict,
    output_type,
    output_str,
    part_1,
    part_2,
    part_3,
    part_4,
):
    tc = TC(timecode_value, timecode_type, fps, drop_frame, strict)
    assert tc.timecode_output(output_type) == output_str
    assert tc.timecode_output(output_type, output_part=1) == part_1
    assert tc.timecode_output(output_type, output_part=2) == part_2
    assert tc.timecode_output(output_type, output_part=3) == part_3
    assert tc.timecode_output(output_type, output_part=4) == part_4


def test_print(tc_data, capsys):
    tc = TC(*tc_data)
    print(tc, end="")
    print_output = capsys.readouterr()
    assert print_output.out == tc_data[0]


@pytest.fixture()
def neg_result(request):
    neg_result_data = {
        "00:00:01:00": "23:59:59:00",
        "1000": "10356632",
        "1.0": "86399.0",
        "00:01:00;02": "23:58:59;28",
        "01:00:00,123": "22:59:59,877",
    }
    tc_value = request.node.funcargs["tc_data"][0]
    print(tc_value)
    return neg_result_data.get(tc_value)


def test_neg(tc_data, neg_result):
    tc = TC(*tc_data)
    tc = -tc
    assert tc.timecode_output() == neg_result


@pytest.fixture(
    params=[
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("23:59:59:00", "auto", 24, False, False),
            ("00:00:00:00", "auto", 24, False, True),
        ),
        (
            ("1000", "auto", 119.88, True, True),
            ("120", "auto", 119.88, True, True),
            ("1120", "auto", 119.88, True, True),
        ),
        pytest.param(
            (
                ("1000", "auto", 119.88, True, True),
                ("1s", "auto", 119.88, True, True),
                ("1120", "auto", 119.88, True, True),
            ),
            marks=pytest.mark.xfail,
        ),
        (
            ("1s", "auto", Fraction(60000, 1001), True, True),
            ("1.0", "auto", Fraction(60000, 1001), True, True),
            ("2s", "auto", Fraction(60000, 1001), True, True),
        ),
        (
            ("00:00:59;29", "auto", 29.97, True, True),
            ("00:00:00;01", "auto", 29.97, True, True),
            ("00:01:00;02", "auto", 29.97, True, True),
        ),
        (
            ("01:00:00,123", "auto", 24, False, True),
            ("01:00:00,878", "auto", 24, False, True),
            ("02:00:01,001", "auto", 24, False, True),
        ),
    ],
    ids=["smpte", "frame", "frame_xfail", "time", "smpte_df", "srt"],
)
def plus_tc_data(request):
    return [TC(*request.param[i]) for i in range(3)]


def test_plus_tc(plus_tc_data):
    tc_plus = plus_tc_data[0] + plus_tc_data[1]
    assert tc_plus == plus_tc_data[2]


@pytest.fixture(
    params=[
        (
            ("00:00:00:23", "auto", 24, False, True),
            1,
            ("00:00:01:00", "auto", 24, False, True),
        ),
        (
            ("1000", "auto", 119.88, True, True),
            111,
            ("1111", "auto", 119.88, True, True),
        ),
        pytest.param(
            (
                ("1s", "auto", Fraction(60000, 1001), True, True),
                60,
                ("2s", "auto", Fraction(60000, 1001), True, True),
            ),
            marks=pytest.mark.xfail,
        ),
        (
            ("00:00:59;29", "auto", 29.97, True, True),
            1,
            ("00:01:00;02", "auto", 29.97, True, True),
        ),
        (
            ("01:00:00,123", "auto", 24, False, True),
            24,
            ("01:00:01,123", "auto", 24, False, True),
        ),
        (
            ("00:00:00:23", "auto", 24, False, True),
            1.0,
            ("00:00:01:23", "auto", 24, False, True),
        ),
        pytest.param(
            (
                ("1000", "auto", 119.88, True, True),
                1.0,
                ("1120", "auto", 119.88, True, True),
            ),
            marks=pytest.mark.xfail,
        ),
        (
            ("1s", "auto", Fraction(60000, 1001), True, True),
            60.0,
            ("61s", "auto", Fraction(60000, 1001), True, True),
        ),
        pytest.param(
            (
                ("00:00:59;29", "auto", 29.97, True, True),
                1.0,
                ("00:01:01;01", "auto", 29.97, True, True),
            ),
            marks=pytest.mark.xfail,
        ),
        (
            ("01:00:00,123", "auto", 24, False, True),
            0.877,
            ("01:00:01,000", "auto", 24, False, True),
        ),
        pytest.param(
            (
                ("00:09:59;00", "auto", 29.97, True, True),
                Fraction(1000, 1001),
                ("00:10:00;00", "auto", 29.97, True, True),
            ),
            marks=pytest.mark.xfail,
        ),
    ],
    ids=[
        "smpte_int",
        "frame_int",
        "time_int_xfail",
        "smpte_df_int",
        "srt_int",
        "smpte_float",
        "frame_float_xfail",
        "time_float",
        "smpte_df_float",
        "srt_float",
        "smpte_df_fraction_xfail",
    ],
)
def plus_num_data(request):
    return [TC(*request.param[0]), request.param[1], TC(*request.param[2])]


def test_plus_num(plus_num_data):
    tc_plus = plus_num_data[0] + plus_num_data[1]
    assert tc_plus == plus_num_data[2]


@pytest.fixture(
    params=[
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("00:00:02:00", "auto", 24, False, False),
            ("23:59:59:00", "auto", 24, False, True),
        ),
        (
            ("1000", "auto", 119.88, True, False),
            ("1001", "auto", 119.88, True, False),
            ("-1", "auto", 119.88, True, False),
        ),
        (
            ("2s", "auto", Fraction(60000, 1001), True, True),
            ("1.0", "auto", Fraction(60000, 1001), True, True),
            ("1s", "auto", Fraction(60000, 1001), True, True),
        ),
        (
            ("00:00:59;29", "auto", 29.97, True, True),
            ("1", "auto", 29.97, True, True),
            ("00:00:59;28", "auto", 29.97, True, True),
        ),
        (
            ("00:00:00,100", "auto", 24, False, True),
            ("00:00:01,000", "auto", 24, False, True),
            ("23:59:59,100", "auto", 24, False, True),
        ),
    ],
    ids=["smpte", "frame", "time", "smpte_df", "srt"],
)
def sub_tc_data(request):
    return [TC(*request.param[i]) for i in range(3)]


def test_sub_tc(sub_tc_data):
    tc_sub = sub_tc_data[0] - sub_tc_data[1]
    assert tc_sub == sub_tc_data[2]


@pytest.fixture(
    params=[
        (
            ("00:00:00:23", "auto", 24, False, True),
            23,
            ("00:00:00:00", "auto", 24, False, True),
        ),
        (
            ("1000", "auto", 119.88, True, False),
            1001,
            ("-1", "auto", 119.88, True, False),
        ),
        pytest.param(
            (
                ("1s", "auto", Fraction(60000, 1001), True, True),
                60,
                ("0s", "auto", Fraction(60000, 1001), True, True),
            ),
            marks=pytest.mark.xfail,
        ),
        (
            ("00:00:59;29", "auto", 29.97, True, True),
            1,
            ("00:00:59;28", "auto", 29.97, True, True),
        ),
        (
            ("01:00:00,123", "auto", 24, False, True),
            24,
            ("00:59:59,123", "auto", 24, False, True),
        ),
        (
            ("00:00:00:23", "auto", 24, False, True),
            1.0,
            ("23:59:59:23", "auto", 24, False, True),
        ),
        (("1000", "auto", 120, True, True), 1.0, ("880", "auto", 120, True, True)),
        (("1s", "auto", 60, True, True), 60.0, ("86341s", "auto", 60, True, True)),
        pytest.param(
            (
                ("00:01:01;02", "auto", 29.97, True, True),
                1.0,
                ("00:01:00;00", "auto", 29.97, True, True),
            ),
            marks=pytest.mark.xfail,
        ),
        (
            ("01:00:00,123", "auto", 24, False, True),
            -0.123,
            ("01:00:00,246", "auto", 24, False, True),
        ),
    ],
    ids=[
        "smpte_int",
        "frame_int",
        "time_int_xfail",
        "smpte_df_int",
        "srt_int",
        "smpte_float",
        "frame_float_xfail",
        "time_float",
        "smpte_df_float",
        "srt_float",
    ],
)
def sub_num_data(request):
    return [TC(*request.param[0]), request.param[1], TC(*request.param[2])]


def test_sub_num(sub_num_data):
    tc_sub = sub_num_data[0] - sub_num_data[1]
    assert tc_sub == sub_num_data[2]


@pytest.fixture(
    params=[
        (
            23,
            ("00:00:00:23", "auto", 24, False, True),
            ("00:00:00:00", "auto", 24, False, True),
        ),
        (
            1001,
            ("1002", "auto", 119.88, True, False),
            ("-1", "auto", 119.88, True, False),
        ),
        pytest.param(
            (
                60,
                ("1s", "auto", Fraction(60000, 1001), True, True),
                ("0s", "auto", Fraction(60000, 1001), True, True),
            ),
            marks=pytest.mark.xfail,
        ),
        (
            1800,
            ("00:00:59;29", "auto", 29.97, True, True),
            ("00:00:00;01", "auto", 29.97, True, True),
        ),
        (
            24,
            ("00:00:00,123", "auto", 24, False, True),
            ("00:00:00,877", "auto", 24, False, True),
        ),
        (
            1.0,
            ("00:00:00:23", "auto", 24, False, True),
            ("00:00:00:01", "auto", 24, False, True),
        ),
        (10.0, ("1000", "auto", 120, True, True), ("200", "auto", 120, True, True)),
        (1.0, ("60s", "auto", 60, True, True), ("86341s", "auto", 60, True, True)),
        (
            0.123,
            ("01:00:00,123", "auto", 24, False, True),
            ("23:00:00,000", "auto", 24, False, True),
        ),
    ],
    ids=[
        "smpte_int",
        "frame_int",
        "time_int_xfail",
        "smpte_df_int",
        "srt_int",
        "smpte_float",
        "frame_float_xfail",
        "time_float",
        "srt_float",
    ],
)
def rsub_num_data(request):
    return [request.param[0], TC(*request.param[1]), TC(*request.param[2])]


def test_rsub_num(rsub_num_data):
    tc_sub = rsub_num_data[0] - rsub_num_data[1]
    assert tc_sub == rsub_num_data[2]


@pytest.fixture(
    params=[
        (
            ("00:00:00:23", "auto", 24, False, True),
            2,
            ("00:00:01:22", "auto", 24, False, True),
        ),
        (
            ("1002", "auto", 119.88, True, False),
            2,
            ("2004", "auto", 119.88, True, False),
        ),
        (
            ("1s", "auto", Fraction(60000, 1001), True, True),
            60,
            ("60s", "auto", Fraction(60000, 1001), True, True),
        ),
        (
            ("00:01:00;02", "auto", 29.97, True, True),
            10,
            ("00:10:00;18", "auto", 29.97, True, True),
        ),
        (
            ("00:00:00,123", "auto", 24, False, True),
            10,
            ("00:00:01,230", "auto", 24, False, True),
        ),
        (
            ("00:00:00:00", "auto", 24, False, True),
            10000.11,
            ("00:00:00:00", "auto", 24, False, True),
        ),
        (("1000", "auto", 120, True, True), 1.5, ("1500", "auto", 120, True, True)),
        (("60s", "auto", 60, True, True), 1.5, ("90s", "auto", 60, True, True)),
        (
            ("01:00:00,000", "auto", 24, False, True),
            1.5,
            ("01:30:00,000", "auto", 24, False, True),
        ),
    ],
    ids=[
        "smpte_int",
        "frame_int",
        "time_int",
        "smpte_df_int",
        "srt_int",
        "smpte_float",
        "frame_float",
        "time_float",
        "srt_float",
    ],
)
def mul_num_data(request):
    return [TC(*request.param[0]), request.param[1], TC(*request.param[2])]


def test_mul(mul_num_data):
    tc_mul = mul_num_data[0] * mul_num_data[1]
    tc_rmul = mul_num_data[1] * mul_num_data[0]
    assert tc_mul == mul_num_data[2]
    assert tc_rmul == mul_num_data[2]


def test_mul_xfail():
    from dftt_timecode.error import DFTTTimecodeOperatorError

    tc_1 = TC("00:00:00:23", "auto", 24, False, True)
    tc_2 = TC("00:11:45:14", "auto", 24, False, True)
    with pytest.raises(DFTTTimecodeOperatorError):
        _ = tc_1 * tc_2


@pytest.fixture(
    params=[
        (
            ("00:00:01:00", "auto", 24, False, True),
            2,
            ("00:00:00:12", "auto", 24, False, True),
        ),
        (
            ("114514", "auto", 119.88, True, False),
            2,
            ("57257", "auto", 119.88, True, False),
        ),
        (
            ("60s", "auto", Fraction(60000, 1001), True, True),
            60,
            ("1s", "auto", Fraction(60000, 1001), True, True),
        ),
        (
            ("00:01:00;02", "auto", 29.97, True, True),
            0.1,
            ("00:10:00;18", "auto", 29.97, True, True),
        ),
        (
            ("00:00:01,234", "auto", 24, False, True),
            Fraction(1, 2),
            ("00:00:02,468", "auto", 24, False, True),
        ),
        (
            ("00:00:00:00", "auto", 24, False, True),
            10000.11,
            ("00:00:00:00", "auto", 24, False, True),
        ),
        (("1000", "auto", 120, True, True), 2.5, ("400", "auto", 120, True, True)),
        (("60s", "auto", 60, True, True), 1.5, ("40s", "auto", 60, True, True)),
        (
            ("01:00:00,000", "auto", 24, False, True),
            0.5,
            ("02:00:00,000", "auto", 24, False, True),
        ),
    ],
    ids=[
        "smpte_int",
        "frame_int",
        "time_int",
        "smpte_df_int",
        "srt_int",
        "smpte_float",
        "frame_float",
        "time_float",
        "srt_float",
    ],
)
def div_num_data(request):
    return [TC(*request.param[0]), request.param[1], TC(*request.param[2])]


def test_div(div_num_data):
    tc_div = div_num_data[0] / div_num_data[1]
    assert tc_div == div_num_data[2]
    from dftt_timecode.error import DFTTTimecodeOperatorError

    with pytest.raises(DFTTTimecodeOperatorError):
        _ = div_num_data[1] / div_num_data[0]


@pytest.mark.parametrize(
    argnames="tc_value,compare_tc_value",
    argvalues=[
        pytest.param(
            ("00:00:01:00", "auto", 24, False, True),
            ("00:00:01:00", "auto", 25, False, True),
            marks=pytest.mark.xfail(raises=dftt_errors.DFTTTimecodeOperatorError),
        ),
        (("00:00:01:00", "auto", 24, False, True), ("24", "auto", 24, False, True)),
        (
            ("00:10:00:00", "auto", 29.97, True, True),
            ("600.0", "auto", 29.97, True, True),
        ),
        (
            ("00:00:01:60", "auto", 120, False, True),
            ("00:00:01,500", "auto", 120, False, True),
        ),
    ],
    ids=["smpte_smpte_xfail", "smpte_frame", "smpte_time", "smpte_srt"],
)
def test_eq_tc(tc_value, compare_tc_value):
    assert TC(*tc_value) == TC(*compare_tc_value)


@pytest.mark.parametrize(
    argnames="tc_value,compare_num",
    argvalues=[
        (("00:00:01:00", "auto", 24, False, True), 24),
        (("114514", "auto", 24, False, True), 114514),
        pytest.param(("60s", "auto", 29.97, True, True), 1799, marks=pytest.mark.xfail),
        (("00:00:01,500", "auto", 120, False, True), 180),
        (("00:00:01:00", "auto", 24, False, True), 1.0),
        (("2400", "auto", 24, False, True), 100.0),
        (("60s", "auto", 29.97, True, True), 60.0),
        (("00:00:01,500", "auto", 120, False, True), 1.5),
    ],
    ids=[
        "smpte_int",
        "frame_int",
        "time_int_xfail",
        "srt_int",
        "smpte_float",
        "frame_float",
        "time_float",
        "srt_float",
    ],
)
def test_eq_num(tc_value, compare_num):
    assert TC(*tc_value) == compare_num


@pytest.mark.parametrize(
    argnames="tc_value,compare_value,xvalue",
    argvalues=[
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("00:00:00:22", "auto", 24, False, True),
            True,
        ),
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("15", "auto", 24, False, True),
            True,
        ),
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("1.0", "auto", 24, False, True),
            False,
        ),
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("00:00:00,500", "auto", 24, False, True),
            True,
        ),
        (("00:00:01:00", "auto", 24, False, True), 22, True),
        (("1919", "auto", 24, False, True), 114514, False),
        (("2s", "auto", 24, False, True), 24, True),
        (("00:00:01,500", "auto", 24, False, True), 24, True),
        (("00:00:01:00", "auto", 24, False, True), 0.5, True),
        (("24", "auto", 24, False, True), 24, False),
        (("5s", "auto", 24, False, True), 0.0, True),
        (("00:00:01,233", "auto", 24, False, True), 1.0, True),
    ],
    ids=[
        "smpte_smpte",
        "smpte_frame",
        "smpte_time",
        "smpte_srt",
        "smpte_int",
        "frame_int",
        "time_int",
        "srt_int",
        "smpte_float",
        "frame_float",
        "time_float",
        "srt_float",
    ],
)
def test_gt(tc_value, compare_value, xvalue):
    tc = TC(*tc_value)
    from numbers import Number

    if isinstance(compare_value, Number):
        assert (tc > compare_value) == xvalue
    elif isinstance(compare_value, tuple):
        compare_tc = TC(*compare_value)
        assert (tc > compare_tc) == xvalue


@pytest.mark.parametrize(
    argnames="tc_value,compare_value,xvalue",
    argvalues=[
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("00:00:00:22", "auto", 24, False, True),
            True,
        ),
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("15", "auto", 24, False, True),
            True,
        ),
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("1.0", "auto", 24, False, True),
            True,
        ),
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("00:00:00,500", "auto", 24, False, True),
            True,
        ),
        (("00:00:01:00", "auto", 24, False, True), 22, True),
        (("1919", "auto", 24, False, True), 114514, False),
        (("2s", "auto", 24, False, True), 24, True),
        (("00:00:01,500", "auto", 24, False, True), 24, True),
        (("00:00:01:00", "auto", 24, False, True), 0.5, True),
        (("24", "auto", 24, False, True), 24, True),
        (("5s", "auto", 24, False, True), 0.0, True),
        (("00:00:01,233", "auto", 24, False, True), 1.0, True),
    ],
    ids=[
        "smpte_smpte",
        "smpte_frame",
        "smpte_time",
        "smpte_srt",
        "smpte_int",
        "frame_int",
        "time_int",
        "srt_int",
        "smpte_float",
        "frame_float",
        "time_float",
        "srt_float",
    ],
)
def test_ge(tc_value, compare_value, xvalue):
    tc = TC(*tc_value)
    from numbers import Number

    if isinstance(compare_value, Number):
        assert (tc >= compare_value) == xvalue
    elif isinstance(compare_value, tuple):
        compare_tc = TC(*compare_value)
        assert (tc >= compare_tc) == xvalue


@pytest.mark.parametrize(
    argnames="tc_value,compare_value,xvalue",
    argvalues=[
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("00:00:00:22", "auto", 24, False, True),
            False,
        ),
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("15", "auto", 24, False, True),
            False,
        ),
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("1.0", "auto", 24, False, True),
            False,
        ),
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("00:00:00,500", "auto", 24, False, True),
            False,
        ),
        (("00:00:01:00", "auto", 24, False, True), 22, False),
        (("1919", "auto", 24, False, True), 114514, True),
        (("2s", "auto", 24, False, True), 999, True),
        (("00:00:01,500", "auto", 24, False, True), 48, True),
        (("00:00:01:00", "auto", 24, False, True), 2.0, True),
        (("24", "auto", 24, False, True), 1.0, False),
        (("0.0", "auto", 24, False, True), 5.0, True),
        (("00:00:01,233", "auto", 24, False, True), 2.0, True),
    ],
    ids=[
        "smpte_smpte",
        "smpte_frame",
        "smpte_time",
        "smpte_srt",
        "smpte_int",
        "frame_int",
        "time_int",
        "srt_int",
        "smpte_float",
        "frame_float",
        "time_float",
        "srt_float",
    ],
)
def test_lt(tc_value, compare_value, xvalue):
    tc = TC(*tc_value)
    from numbers import Number

    if isinstance(compare_value, Number):
        assert (tc < compare_value) == xvalue
    elif isinstance(compare_value, tuple):
        compare_tc = TC(*compare_value)
        assert (tc < compare_tc) == xvalue


@pytest.mark.parametrize(
    argnames="tc_value,compare_value,xvalue",
    argvalues=[
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("00:00:00:22", "auto", 24, False, True),
            False,
        ),
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("15", "auto", 24, False, True),
            False,
        ),
        pytest.param(
            ("00:00:01:00", "auto", 24, False, True),
            ("1.0", "auto", 25, False, True),
            True,
            marks=pytest.mark.xfail(raises=dftt_errors.DFTTTimecodeOperatorError),
        ),
        (
            ("00:00:01:00", "auto", 24, False, True),
            ("00:00:00,500", "auto", 24, False, True),
            False,
        ),
        (("00:00:01:00", "auto", 24, False, True), 22, False),
        (("1919", "auto", 24, False, True), 114514, True),
        (("2s", "auto", 24, False, True), 999, True),
        (("00:00:01,500", "auto", 24, False, True), 48, True),
        (("00:00:01:00", "auto", 24, False, True), 2.0, True),
        (("24", "auto", 24, False, True), 1.0, True),
        (("0.0", "auto", 24, False, True), 5.0, True),
        (("00:00:01,233", "auto", 24, False, True), 2.0, True),
    ],
    ids=[
        "smpte_smpte",
        "smpte_frame",
        "smpte_time",
        "smpte_srt",
        "smpte_int",
        "frame_int",
        "time_int",
        "srt_int",
        "smpte_float",
        "frame_float",
        "time_float",
        "srt_float",
    ],
)
def test_lte(tc_value, compare_value, xvalue):
    tc = TC(*tc_value)
    from numbers import Number

    if isinstance(compare_value, Number):
        assert (tc <= compare_value) == xvalue
    elif isinstance(compare_value, tuple):
        compare_tc = TC(*compare_value)
        assert (tc <= compare_tc) == xvalue


@pytest.mark.parametrize(
    argnames="tc_value,xvalue",
    argvalues=[
        (("00:00:01:00", "auto", 24, False, True), 1.0),
        (("00:01:00;02", "auto", 29.97, True, True), float(Fraction(1800 / 29.97))),
        (("48", "auto", 24, False, True), 2.0),
        (("114514s", "auto", 24, False, True), 114514.0),
        (("00:00:01,500", "auto", 24, False, True), 1.5),
    ],
    ids=["smpte", "smpte_df", "frame", "time", "srt"],
)
def test_float(tc_value, xvalue):
    tc = TC(*tc_value)
    assert float(tc) == pytest.approx(xvalue, 5)


@pytest.mark.parametrize(
    argnames="tc_value,xvalue",
    argvalues=[
        (("00:00:01:00", "auto", 24, False, True), 24),
        (("00:01:00;02", "auto", 29.97, True, True), 1800),
        (("114514", "auto", 24, False, True), 114514),
        (("2.0s", "auto", 24, False, True), 48),
        (("00:00:01,500", "auto", 24, False, True), 36),
    ],
    ids=["smpte", "smpte_df", "frame", "time", "srt"],
)
def test_int(tc_value, xvalue):
    tc = TC(*tc_value)
    assert int(tc) == xvalue


@pytest.mark.parametrize(
    argnames="tc_value,sample_rate,xvalue",
    argvalues=[
        (("00:00:01:00", "auto", 24, False, True), 48000, 48000),
        (("00:00:01:01", "auto", 24, False, True), 48000, 50000),
        (("00:00:01:01", "auto", 24, False, True), 44100, 45937),
    ],
    ids=["ideal", "single_frame", "24fps_44100"],
)
def test_audio_sample_count(tc_value, sample_rate, xvalue):
    tc = TC(*tc_value)
    assert tc.get_audio_sample_count(sample_rate) == xvalue

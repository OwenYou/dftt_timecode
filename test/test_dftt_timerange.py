from dftt_timecode import DfttTimeRange as TC_Range
from dftt_timecode import DfttTimecode as TC


import pytest


@pytest.mark.parametrize(
    argnames="_start_tc,_end_tc,_fps",
    argvalues=[
        (TC('00:00:00:00','auto',fps=24),TC('00:00:00:20','auto',fps=24),24),
        (TC('00:00:00:00','auto',fps=24),1.0,24),
        (1.0,TC('00:00:02:20','auto',fps=24),24),
        (1.0,50,24)
        ],
    ids=['TC_TC','TC_Other','Other_TC','Other_Other'])
def test_init(_start_tc,_end_tc,_fps):
    tc_range=TC_Range(start_tc=_start_tc,end_tc=_end_tc,fps=_fps)
    assert isinstance(tc_range,TC_Range)
    for tc in tc_range:
        assert isinstance(tc,TC)
    
    
    
@pytest.mark.parametrize(
    'range_value,x_duration_value', 
    [
    ({'start_tc':TC('00:00:00:00','auto',fps=24),'end_tc':TC('00:00:01:00','auto',fps=24)},1),
    ({'start_tc':TC('00:00:00:00','auto',fps=24),'end_tc':TC('00:00:01:00','auto',fps=24),'forward':False},86399), 
    ({'start_tc':TC('23:59:59:00','auto',fps=24),'end_tc':TC('00:00:01:00','auto',fps=24)},2),
    ({'start_tc':TC('00:00:01:00','auto',fps=24),'end_tc':TC('23:59:59:00','auto',fps=24),'forward':False},2),
    
    ({'start_tc':TC('00:00:00:00','auto',fps=24),'end_tc':2.0},2),
    ({'start_tc':TC('00:00:02:00','auto',fps=24),'end_tc':0.0,'forward':False},2),
    ({'start_tc':TC('23:59:59:00','auto',fps=24),'end_tc':'00:00:00:00'},1),
    ({'start_tc':TC('00:00:01:00','auto',fps=24),'end_tc':'23:59:59:00','forward':False},2),  
    
    ({'start_tc':'2s'           ,'end_tc':TC('4.0','auto',fps=24)},2),
    ({'start_tc':2.0            ,'end_tc':TC('00:00:00:00','auto',fps=24),'forward':False},2),
    ({'start_tc':'86399s'       ,'end_tc':TC('00:00:00:00','auto',fps=24)},1),
    ({'start_tc':'00:00:01:00'  ,'end_tc':TC('23:59:59:00','auto',fps=24),'forward':False},2),
    
    ({'start_tc':'2s'           ,'end_tc':4.0},2),
    ({'start_tc':2.0            ,'end_tc':0,'forward':False},2),
    ({'start_tc':'86399s'       ,'end_tc':0},1),
    ({'start_tc':'00:00:01:00'  ,'end_tc':'23:59:59:00','forward':False},2),
    
    ],
    ids=['TC_TC','TC_TC_Reverse','TC_TC_Midnight','TC_TC_Reverse_Mignight',
         'TC_Other','TC_Other_Reverse','TC_Other_Midnight','TC_Other_Reverse_Mignight',
         'Other_TC','Other_TC_Reverse','Other_TC_Midnight','Other_TC_Reverse_Mignight',
         'Other_Other','Other_Other_Reverse','Other_Other_Midnight','Other_Other_Reverse_Mignight',
    ])
def test_duration(range_value,x_duration_value):
    tc_range=TC_Range(**range_value)
    assert tc_range.duration == x_duration_value
    

@pytest.mark.parametrize(
   argnames="range_value,x_framecount_value",
   argvalues=[
    ({'start_tc':TC('00:00:00:00','auto',fps=24),'end_tc':TC('00:00:01:01','auto',fps=24)},25),
    ({'start_tc':TC('00:00:00:00','auto',fps=24),'end_tc':TC('00:00:00:01','auto',fps=24),'forward':False},2073599), 
    ({'start_tc':TC('23:59:59:00','auto',fps=24),'end_tc':TC('00:00:00:01','auto',fps=24)},2),
    ({'start_tc':TC('00:00:01:00','auto',fps=24),'end_tc':TC('23:59:59:00','auto',fps=24),'forward':False},2),
    
    ({'start_tc':TC('00:00:00:00','auto',fps=24),'end_tc':2.0},2),
    ({'start_tc':TC('00:00:02:00','auto',fps=24),'end_tc':0.0,'forward':False},2),
    ({'start_tc':TC('23:59:59:00','auto',fps=24),'end_tc':'00:00:00:00'},1),
    ({'start_tc':TC('00:00:01:00','auto',fps=24),'end_tc':'23:59:59:00','forward':False},2),  
    
    ({'start_tc':'2s'           ,'end_tc':TC('4.0','auto',fps=24)},2),
    ({'start_tc':2.0            ,'end_tc':TC('00:00:00:00','auto',fps=24),'forward':False},2),
    ({'start_tc':'86399s'       ,'end_tc':TC('00:00:00:00','auto',fps=24)},1),
    ({'start_tc':'00:00:01:00'  ,'end_tc':TC('23:59:59:00','auto',fps=24),'forward':False},2),
    
    ({'start_tc':'2s'           ,'end_tc':4.0},2),
    ({'start_tc':2.0            ,'end_tc':0,'forward':False},2),
    ({'start_tc':'86399s'       ,'end_tc':0},1),
    ({'start_tc':'00:00:01:00'  ,'end_tc':'23:59:59:00','forward':False},2),
       ],
   ids=['TC_TC','TC_TC_Reverse','TC_TC_Midnight','TC_TC_Reverse_Mignight',
         'TC_Other','TC_Other_Reverse','TC_Other_Midnight','TC_Other_Reverse_Mignight',
         'Other_TC','Other_TC_Reverse','Other_TC_Midnight','Other_TC_Reverse_Mignight',
         'Other_Other','Other_Other_Reverse','Other_Other_Midnight','Other_Other_Reverse_Mignight',])
def test_framecount(range_value,x_framecount_value):
    tc_range=TC_Range(**range_value)
    assert tc_range.framecount == x_framecount_value
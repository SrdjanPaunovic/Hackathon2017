"""This module is main module for contestant's solution."""

from hackathon.utils.control import Control
from hackathon.utils.utils import ResultsMessage, DataMessage, PVMode, \
    TYPHOON_DIR, config_outs
from hackathon.framework.http_server import prepare_dot_dir

cheapPrice = 100
currentIteration = 0
maxIteration = 60 * 7

def worker(msg: DataMessage) -> ResultsMessage:
    """TODO: This function should be implemented by contestants."""
    # Details about DataMessage and ResultsMessage objects can be found in /utils/utils.py
    global cheapPrice
    global currentIteration
    global maxIteration

    if not msg.grid_status:
        currentIteration = 0

    currentIteration += 1

    if msg.buying_price < cheapPrice:
        cheapPrice = msg.buying_price

    if msg.grid_status == True:
        return gridOn(msg)
    else:
        return gridOff(msg)

    # Dummy result is returned in every cycle here
    return ResultsMessage(data_msg=msg,
                          load_one=True,
                          load_two=True,
                          load_three=True,
                          power_reference=0.0,
                          pv_mode=PVMode.ON)

def gridOn(msg: DataMessage) -> ResultsMessage:
    if currentIteration < maxIteration:
        if msg.bessSOC < 1 and msg.buying_price <= cheapPrice:
            return ResultsMessage(data_msg=msg,
                                  load_one=True,
                                  load_two=True,
                                  load_three=True,
                                  power_reference=-6.0,
                                  pv_mode=PVMode.ON)
        elif msg.buying_price > cheapPrice:
            return ResultsMessage(data_msg=msg,
                                  load_one=True,
                                  load_two=True,
                                  load_three=True,
                                  power_reference=2.0,
                                  pv_mode=PVMode.ON)
        else:
            return ResultsMessage(data_msg=msg,
                                  load_one=True,
                                  load_two=True,
                                  load_three=True,
                                  power_reference=0.0,
                                  pv_mode=PVMode.ON)
    else:
        if msg.bessSOC < 1 and msg.buying_price <= cheapPrice:
            return ResultsMessage(data_msg=msg,
                                  load_one=True,
                                  load_two=True,
                                  load_three=True,
                                  power_reference=-6.0,
                                  pv_mode=PVMode.ON)
        elif msg.bessSOC > 0.6 and msg.buying_price > cheapPrice:
            return ResultsMessage(data_msg=msg,
                                  load_one=True,
                                  load_two=True,
                                  load_three=True,
                                  power_reference=2.0,
                                  pv_mode=PVMode.ON)
        elif msg.bessSOC < 0.6 and msg.buying_price > cheapPrice:
            return ResultsMessage(data_msg=msg,
                                  load_one=True,
                                  load_two=True,
                                  load_three=False,
                                  power_reference=0.0,
                                  pv_mode=PVMode.ON)
        else:
            return ResultsMessage(data_msg=msg,
                                  load_one=True,
                                  load_two=True,
                                  load_three=True,
                                  power_reference=0.0,
                                  pv_mode=PVMode.ON)

def gridOff(msg: DataMessage) -> ResultsMessage:
    if msg.current_load <= msg.solar_production:
        return ResultsMessage(data_msg=msg,
                              load_one=True,
                              load_two=True,
                              load_three=True,
                              power_reference=0.0,
                              pv_mode=PVMode.ON)
    elif msg.current_load <= msg.solar_production + 6:
        return ResultsMessage(data_msg=msg,
                              load_one=True,
                              load_two=True,
                              load_three=True,
                              power_reference=msg.current_load - msg.solar_production,
                              pv_mode=PVMode.ON)
    elif msg.current_load - 0.3*msg.current_load <= msg.solar_production + 6:
        return ResultsMessage(data_msg=msg,
                              load_one=True,
                              load_two=True,
                              load_three=False,
                              power_reference=msg.current_load - msg.solar_production,
                              pv_mode=PVMode.ON)
    elif msg.current_load - 0.5*msg.current_load <= msg.solar_production + 6:
        return ResultsMessage(data_msg=msg,
                              load_one=True,
                              load_two=False,
                              load_three=True,
                              power_reference=6.0,
                              pv_mode=PVMode.ON)
    elif msg.current_load - 0.5*msg.current_load - 0.3*msg.current_load <= msg.solar_production + 6:
        return ResultsMessage(data_msg=msg,
                              load_one=True,
                              load_two=False,
                              load_three=False,
                              power_reference=6.0,
                              pv_mode=PVMode.ON)
    else:
        return ResultsMessage(data_msg=msg,
                              load_one=False,
                              load_two=True,
                              load_three=True,
                              power_reference=6.0,
                              pv_mode=PVMode.ON)

def run(args) -> None:
    prepare_dot_dir()
    config_outs(args, 'solution')

    cntrl = Control()

    for data in cntrl.get_data():
        cntrl.push_results(worker(data))

"""This module is main module for contestant's solution."""

from hackathon.utils.control import Control
from hackathon.utils.utils import ResultsMessage, DataMessage, PVMode, \
    TYPHOON_DIR, config_outs
from hackathon.framework.http_server import prepare_dot_dir

charging = False

def worker(msg: DataMessage) -> ResultsMessage:
    """TODO: This function should be implemented by contestants."""
    # Details about DataMessage and ResultsMessage objects can be found in /utils/utils.py

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
    global charging

    pwr_reference = 0.0

    if msg.bessSOC < 0.6:
        charging = True
    elif msg.bessSOC == 1.0:
        charging = False

    if charging:
        if msg.buying_price < msg.selling_price:
             pwr_reference = - 6.0
        elif msg.solar_production > 0.0:
             pwr_reference = -msg.solar_production
        else:
             pwr_reference = 0.0
    else:
        pwr_reference = 6.0

    print(pwr_reference)
    return ResultsMessage(data_msg=msg,
                            load_one=True,
                            load_two=True,
                            load_three=True,
                            power_reference = pwr_reference,
                            pv_mode=PVMode.ON)

def gridOff(msg: DataMessage) -> ResultsMessage:
    if msg.current_load <= msg.solar_production:
        return ResultsMessage(data_msg=msg,
                              load_one=True,
                              load_two=True,
                              load_three=True,
                              power_reference=0.0,
                              pv_mode=PVMode.ON)
    elif msg.current_load <= msg.solar_production + 6.0:
        return ResultsMessage(data_msg=msg,
                              load_one=True,
                              load_two=True,
                              load_three=True,
                              power_reference=msg.current_load - msg.solar_production,
                              pv_mode=PVMode.ON)
    else:
        return ResultsMessage(data_msg=msg,
                              load_one=True,
                              load_two=False,
                              load_three=True,
                              power_reference=6.0,
                              pv_mode=PVMode.ON)

def run(args) -> None:
    prepare_dot_dir()
    config_outs(args, 'solution')

    cntrl = Control()

    for data in cntrl.get_data():
        cntrl.push_results(worker(data))

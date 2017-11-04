"""This module is main module for contestant's solution."""

from hackathon.utils.control import Control
from hackathon.utils.utils import ResultsMessage, DataMessage, PVMode, \
    TYPHOON_DIR, config_outs
from hackathon.framework.http_server import prepare_dot_dir


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
    if msg.bessSOC < 0.8:
        return ResultsMessage(data_msg=msg,
                              load_one=True,
                              load_two=True,
                              load_three=True,
                              power_reference=-0.1,
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
    else:
        return ResultsMessage(data_msg=msg,
                              load_one=True,
                              load_two=True,
                              load_three=False,
                              power_reference=6.0,
                              pv_mode=PVMode.ON)



def run(args) -> None:
    prepare_dot_dir()
    config_outs(args, 'solution')

    cntrl = Control()

    for data in cntrl.get_data():
        cntrl.push_results(worker(data))

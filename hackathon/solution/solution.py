"""This module is main module for contestant's solution."""

from hackathon.utils.control import Control
from hackathon.utils.utils import ResultsMessage, DataMessage, PVMode, \
    TYPHOON_DIR, config_outs
from hackathon.framework.http_server import prepare_dot_dir
from scipy.optimize import minimize
import numpy
charging = False

def batteryUsage(msg: DataMessage) -> float:

    needPower = msg.buying_price*msg.current_load - msg.selling_price*msg.solar_production
    if msg.selling_price == 0:
        return
    return newPower/msg.selling_price

def getParams(msg: DataMessage) :

    k1 = msg.buying_price
    k2 = msg.selling_price
    A = msg.current_load
    B = msg.solar_production

    def f(x):
        loadCost = k1*A*(0.2*x[0]+0.5*x[1]+0.3*x[2])
        penaltyCost = 25.0 - 20.0*x[0] - 4.0*x[1] - x[2]
        generatedPrice = (6.0*x[3] + B)*k2

        return loadCost + 15.0*penaltyCost - generatedPrice
    x0_bounds = ( 0, 1)
    x1_bounds = ( 0, 1)
    x2_bounds = ( 0, 1)
    x3_bounds = ( -1, 1)
    initial_value = numpy.array([1.0,1.0,1.0, -1])
    b = [x0_bounds, x1_bounds, x2_bounds, x3_bounds]
    return minimize(f,x0=initial_value,args=(),method='L-BFGS-B', bounds = b)

# def doLinprog(msg: DataMessage):
#
#
#         k1 = msg.buying_price
#         k2 = msg.selling_price
#         A = msg.current_load
#         B = msg.solar_production
#
#
#         x0_bounds = ( 0, 1)
#         x1_bounds = ( 0, 1)
#         x2_bounds = ( 0, 1)
#         x3_bounds = ( -1, 1)
#         initial_value = numpy.array([1.0,1.0,1.0,0.0])
#         b = [x0_bounds,x1_bounds,x2_bounds,x3_bounds]
#         return minimize(f,x0=initial_value,args=(),method='L-BFGS-B', bounds = b)





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
    #
    # if charging:
    #     if msg.buying_price < msg.selling_price:
    #          pwr_reference = - 6.0
    #     elif msg.solar_production > 0.0:
    #          pwr_reference = -msg.solar_production
    #     else:
    #          pwr_reference = 0.0
    # else:
    #     pwr_reference = 6.0

    x = getParams(msg)
    k1 = msg.buying_price
    k2 = msg.selling_price
    k = float(k1 == 3.0)* 3.0 #koeficient punjenja
    boolVector = x.x == 1.0
    if x.x[3] > 0 and msg.bessSOC > 0.6:
        pwr_reference = float(x.x[3])  # praznjenje
    elif x.x[3] < 0 and msg.bessSOC < 1:
        pwr_reference = 4 * float(x.x[3])    # punjenje

    print(k)
    return ResultsMessage(data_msg=msg,
                            load_one= bool(boolVector[0]),
                            load_two= bool(boolVector[1]),
                            load_three= bool(boolVector[2]),
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

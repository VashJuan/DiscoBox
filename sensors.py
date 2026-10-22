# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Time of Flight distance sensor & onboard LIS3DH accelerometer"""

import board
from digitalio import DigitalInOut
import adafruit_vl53l1x  # "Time of flight", i.e., distance sensor
import adafruit_lis3dh  # accelerometer

from config import verbose


def setup_tof(i2c):
    """Time of Flight - i.e., distance measurement"""
    # https://learn.adafruit.com/adafruit-vl53l1x
    vl53 = adafruit_vl53l1x.VL53L1X(i2c)
    vl53.distance_mode = 1
    vl53.timing_budget = 100

    if verbose:
        print("VL53L1X Simple Test.")
        print("--------------------")
        model_id, module_type, mask_rev = vl53.model_info
        print("Model ID: 0x{:0X}".format(model_id))
        print("Module Type: 0x{:0X}".format(module_type))
        print("Mask Revision: 0x{:0X}".format(mask_rev))
        print("Distance Mode: ", end="")
        if vl53.distance_mode == 1:
            print("SHORT mode")
        elif vl53.distance_mode == 2:
            print("LONG mode")
        else:
            print("UNKNOWN mode")
        print("Timing Budget: {}".format(vl53.timing_budget))
        print("--------------------")

    vl53.start_ranging()
    return vl53


def setup_accelerometer():
    """Onboard i2c LIS3DH accelerometer"""
    # https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout
    i2c = board.I2C()
    int1 = DigitalInOut(board.ACCELEROMETER_INTERRUPT)
    lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, int1=int1)
    # https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout/arduino#accelerometer-ranges-1729247
    lis3dh.range = adafruit_lis3dh.RANGE_2_G
    # https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout/arduino#tap-and-double-tap-detection-1729254
    lis3dh.set_tap(1, 100)  # set_tap(2, THRESHOLD) looks for double taps
    return lis3dh


def read_acceleration(lis3dh):
    """Return (x, y, z) in G"""
    # right side down = increasing X
    # top down ((i.e., mailbox lid open) y ~= 0, closed lid (top up) y ~= -0.9
    # z up to 2 & down to -1??? up for raising, down for lowering
    return [value / adafruit_lis3dh.STANDARD_GRAVITY for value in lis3dh.acceleration]

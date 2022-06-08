import os
from serial import Serial
import logging
import time

serial_port = "COM5"

values_to_capture_in_buffer = 50  # 5sec


serial = Serial(
    port=serial_port,
    baudrate=9600,
)


def in_range(val, start, end):
    if start <= int(val) <= end:
        return True
    else:
        return False


def check_gait_normal(val):
    if in_range(val[0], 640, 1100) and in_range(val[1], 15, 950) and in_range(val[2], 700, 1000) and \
            in_range(val[3], 420, 980) and in_range(val[4], 20, 550) and in_range(val[5], 840, 1100) and \
            in_range(val[6], 15, 1000):
        return True
    else:
        return False


def check_gait_front(val):
    if in_range(val[0], 900, 1050) and in_range(val[1], 25, 850) and in_range(val[2], 500, 1000) and \
            in_range(val[3], 800, 1000) and in_range(val[4], 250, 630) and in_range(val[5], 880, 1100) and \
            in_range(val[6], 14, 600):
        return True
    else:
        return False


def check_gait_back(val):
    if in_range(val[0], 0, 40) and in_range(val[1], 0, 5) and in_range(val[2], 0, 550) and \
            in_range(val[3], 0, 15) and in_range(val[4], 5, 15) and in_range(val[5], 5, 20) and \
            in_range(val[6], 700, 1100):
        return True
    else:
        return False


def predict(arr_list):
    gate_normal_arr = []
    gate_front_arr = []
    gate_back_arr = []

    for arr in arr_list:
        if check_gait_normal(arr):
            gate_normal_arr.append(arr)
        if check_gait_front(arr):
            gate_front_arr.append(arr)
        if check_gait_back(arr):
            gate_back_arr.append(arr)

    print('gait_normal_count', gate_normal_count)
    print('gait_front_count', gate_front_count)
    print('gait_back_count', gate_back_count)


def main():
    serial_status = serial.isOpen()
    logging.debug(f"Serial is: {'Opened' if serial_status else 'NOT Opened'}")
    count = 0
    values_arr = []
    while True:
        incoming_data = str(serial.readline().decode("utf-8"))
        logging.debug(f"serial_in: {incoming_data.strip()}")
        try:
            values = [x.strip() for x in incoming_data.split(',')]
            if count < values_to_capture_in_buffer:
                count += 1
                values_arr.append(values)

            elif count == values_to_capture_in_buffer:
                predict(values_arr)
                count = 0
                values_arr = []

        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()

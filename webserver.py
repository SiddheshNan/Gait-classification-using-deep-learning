import json
import os
import threading
import webbrowser
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from serial import Serial
from tensorflow.keras.models import load_model
import numpy as np
from tornado import websocket, web, ioloop
from abc import ABC

serial_port = "COM10"

values_to_capture_in_buffer = 75  # 5sec

np.set_printoptions(suppress=True)
model = load_model('model.h5', compile=False)
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

serial = Serial(
    port=serial_port,
    baudrate=9600,
)

CHK = True


class WebSocketHandler(websocket.WebSocketHandler, ABC):
    clients = set()

    def check_origin(self, origin):
        return True

    def open(self):
        WebSocketHandler.clients.add(self)

    def on_close(self):
        WebSocketHandler.clients.remove(self)

    @classmethod
    def send_message(cls, message: str):
        if len(cls.clients):
            for client in cls.clients:
                client.write_message(message)

    def on_message(self, message):
        global CHK
        print(f"Msg received from client: {message}")
        if message == 'ok':
            CHK = True


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


def predict(arr_list, data):
    global CHK
    prediction = model.predict(data)
    prediction_new = prediction[0].tolist()

    gate_normal_count = 0
    gate_front_count = 0
    gate_back_count = 0

    for arr in arr_list:
        if check_gait_normal(arr) and prediction_new:
            gate_normal_count += 1
        if check_gait_front(arr) and prediction_new:
            gate_front_count += 1
        if check_gait_back(arr) and prediction_new:
            gate_back_count += 1

    print('Neutral (normal) count:', gate_normal_count)
    print('Pronator (front) count:', gate_front_count)
    print('Supinator (back) count:', gate_back_count)
    print("------------")
    ok = 0
    if gate_normal_count > gate_front_count and gate_normal_count > gate_back_count:
        ok = 1
        print("Gait Classification: Neutral")
        WebSocketHandler.send_message(json.dumps({'detected': 'Neutral'}))
    if gate_front_count > gate_normal_count and gate_front_count > gate_back_count:
        ok = 1
        print("Gait Classification: Pronator")
        WebSocketHandler.send_message(json.dumps({'detected': 'Pronator'}))
    if gate_back_count > gate_normal_count and gate_back_count > gate_front_count:
        ok = 1
        print("Gait Classification: Supinator")
        WebSocketHandler.send_message(json.dumps({'detected': 'Supinator'}))
    if not ok:
        print("Gait Classification: N/A")
        WebSocketHandler.send_message(json.dumps({'detected': 'n/a'}))

    CHK = False
    while not CHK:
        pass
    serial.reset_output_buffer()
    serial.reset_input_buffer()


def main():
    serial_status = serial.isOpen()
    print(f"Serial port is: {'Opened' if serial_status else 'NOT Opened'}")
    if not serial_status:
        exit()
    input("Press Enter to start")
    serial.reset_output_buffer()
    serial.reset_input_buffer()
    count = 0
    values_arr = []

    while True:
        incoming_data = str(serial.readline().decode("utf-8"))
        print(f"Steps: {incoming_data.strip()}")
        WebSocketHandler.send_message(json.dumps({'steps': incoming_data.strip()}))
        try:
            values = [x.strip() for x in incoming_data.split(',')]
            if count < values_to_capture_in_buffer:
                count += 1
                values_arr.append(values)
            elif count == values_to_capture_in_buffer:
                predict(values_arr, data)
                count = 0
                values_arr = []

        except Exception as e:
            print(e)


if __name__ == '__main__':
    tq = threading.Thread(target=main)
    tq.start()
    app = web.Application([
        (r'/ws', WebSocketHandler),
        (r"/(.*)", web.StaticFileHandler, {"path": './static', "default_filename": "index.html"})
    ],
        websocket_ping_interval=10,
        websocket_ping_timeout=30,
        debug=True,
    )
    app.listen(2222)
    io_loop = ioloop.IOLoop.current()
    io_loop.start()



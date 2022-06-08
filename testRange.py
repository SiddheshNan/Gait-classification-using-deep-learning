
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


lines = open("normal.txt", "r").readlines()

gate_normal_count = 0
gate_front_count = 0
gate_back_count = 0

for line in lines:
    arr = str(line).strip().split(",")

    if check_gait_normal(arr):
        gate_normal_count += 1
    if check_gait_front(arr):
        gate_front_count += 1
    if check_gait_back(arr):
        gate_back_count += 1


no_line = len(lines)
print('gate_normal_count', (gate_normal_count * no_line) / 100)
print('gate_front_count', (gate_front_count * no_line) / 100)
print('gate_back_count', (gate_back_count * no_line) / 100)
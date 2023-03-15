import numpy as np
import re
import math

# read file
with open('D:\\11karl\\Masterarbeit\\NX model\\model1.txt', 'r') as f:
    data1 = f.readlines()

#set spindle speed and feed rate
feed_rate = 100
spindle_speed = 1000



# define the transformation parameters
rotation_theta = 0.79
trans_vector = np.array([2.34, -2.76])
d_X = trans_vector[0]
d_Y = trans_vector[1]
initial_position = [1, 2]
X_initial = initial_position[0]
Y_initial = initial_position[1]


new_Gcode = []
for line in data1:
    # store XY value from the last line
    if 'X' in locals():
        X_start_old = X
    if 'Y' in locals():
        Y_start_old = Y
    if 'X_new' in locals():
        X_start_new = X_new
    if 'Y_new' in locals():
        Y_start_new = Y_new

    if re.search(r'X([\d\.-])+(\s+Y([\d\.-]+))?', line):
        # extract X and Y values
        if 'X' in line:
            X = float(re.findall(r"X([\d\.-]+)", line)[0])
        else:
            if 'X_new' in locals():
                X = X_new

        if 'Y' in line:
            Y = float(re.findall(r"Y([\d\.-]+)", line)[0])
        else:
            if 'Y_new' in locals():
                Y = Y_new

        # calculate new value of X and Y
        if 'X' in line:
            X_new = (X - X_initial) * math.cos(rotation_theta) - (Y - Y_initial) * math.sin(rotation_theta) + X + d_X
            line = re.sub(r'X\d+(\.\d+)?', f'X{X_new:.3f}', line)
        else:
            X_new = X

        if 'Y' in line:
            Y_new = (X - X_initial) * math.sin(rotation_theta) + (Y - Y_initial) * math.cos(rotation_theta) + Y + d_Y
            line = re.sub(r'Y[\d\.-]+', f'Y{Y_new:.3f}', line)
        else:
            Y_new = Y

    # check if contains I and J values
    if re.search(r'I([\d\.-])+(\s+J([\d\.-]+))?', line):
        # extract I and J values
        if re.search(r"I([\d\.-]+)", line):
            I = float(re.findall(r"I([\d\.-]+)", line)[0])
        else:
            I = 0

        if re.search(r"J([\d\.-]+)", line):
            J = float(re.findall(r"J([\d\.-]+)", line)[0])
        else:
            J = 0

        X_centre_old = X_start_old + I
        Y_centre_old = Y_start_old + J

        X_centre_new = (X_centre_old - X_initial) * math.cos(rotation_theta) - (Y_centre_old - Y_initial) \
                       * math.sin(rotation_theta) + X_centre_old + d_X
        Y_centre_new = (X_centre_old - X_initial) * math.sin(rotation_theta) + (Y_centre_old - Y_initial) \
                       * math.cos(rotation_theta) + Y_centre_old + d_Y

        I_new = X_centre_new - X_start_new
        J_new = Y_centre_new - Y_start_new

        line = re.sub(r'I[\d\.-]+', f'I{I_new:.3f}', line)
        line = re.sub(r'J[\d\.-]+', f'J{Y_new:.3f}', line)

    # add this line to new G code
    new_Gcode.append(line)

new_line = "G94 F{}\nM03 S{}\n".format(feed_rate, spindle_speed)
line = list(line)
line.insert(4, new_line)
line = ''.join(line)

#print(''.join(new_Gcode))
with open("D:\\11karl\\Masterarbeit\\NX model\\model1_new.txt", "w") as f:
    f.write(''.join(new_Gcode))
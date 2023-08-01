import numpy as np
import re
import math
from sympy import symbols, sqrt, solve
import os

#set spindle speed and feed rate
feed_rate = 100
spindle_speed = 1000

# define the transformation parameters
rotation_theta = 45 * math.pi/180
trans_vector = np.array([1, 2])
d_X = trans_vector[0]
d_Y = trans_vector[1]
initial_position = [0, 0]
X_initial = initial_position[0]
Y_initial = initial_position[1]
i=0

def save_completed_file(file_path):
    # Read the file
    with open(file_path, 'r') as f:
        data = f.read()

    # Extract the file name and extension
    file_name, file_extension = os.path.splitext(file_path)

    # Create a new file name
    new_file_name = file_name + "_completed" + file_extension

    # Save the data to the new file
    #with open(new_file_name, 'w') as f:
    #    f.write(data)

    #print("File saved as", new_file_name)
    return new_file_name

def save_transformed_file(file_path):
    # Read the file
    with open(file_path, 'r') as f:
        data = f.read()

    # Extract the file name and extension
    file_name, file_extension = os.path.splitext(file_path)

    # Create a new file name
    new_file_name = file_name + f"_{trans_vector}_{rotation_theta}" + file_extension

    # Save the data to the new file
    #with open(new_file_name, 'w') as f:
    #    f.write(data)

    #print("File saved as", new_file_name)
    return new_file_name

def circle_center(X_last_old, Y_last_old, X_old, Y_old, I_old, J_old):
    Xc_old = X_last_old + I_old
    Yc_old = Y_last_old + J_old
    r = 0.5 * math.sqrt((Xc_old - X_last_old)**2 + (Yc_old - Y_last_old)**2)
    x_m = (X_last_old + X_old) / 2
    y_m = (Y_last_old + Y_old) / 2
    k = (Y_old - Y_last_old) / (X_old - X_last_old)
    k_m = - 1 / k
    l_m = k_m*()
    x_c = x_m - (Y_old - Y_last_old) / (2 * math.sqrt(k**2 + 1))
    y_c = y_m - (X_old - X_last_old) / (2 * math.sqrt(k**2 + 1))
    return x_c, y_c

#complete XY in each line
file_path = 'D:\\11karl\\Masterarbeit\\NX model\\newtry_onelayer_20mm.txt'
with open(file_path, 'r') as f:
    data2 = f.readlines()
Gcode = []
for line in data2:
    #i=i+1
    #print(i)
    if 'X' in line:
        X = float(re.findall(r"X([\d\.-]+)", line)[0])
    else:
        if 'G40' not in line and 'G91' not in line and 'Z' not in line and 'T00' not in line:
            if 'Y' not in line:
                line = line.strip()+ f' X{X}'
            else:
                match = re.match(r'(^N\d+\b)\s+(Y[\d\.-]+)\s*', line)
                if match:
                    line = f"{match.group(1)} X{X} {match.group(2)}\n"


    if 'Y' in line:
        Y = float(re.findall(r"Y([\d\.-]+)", line)[0])
    else:
        if 'G40' not in line and 'G91' not in line and 'Z' not in line and 'T00' not in line:
            line = line.strip() + f' Y{Y}'+'\n'

    Gcode.append(line)

file_path_completed = save_completed_file(file_path)
with open(file_path_completed, "w") as f:
    f.write(''.join(Gcode))

# read the new file
with open(file_path_completed, 'r') as f:
    data1 = f.readlines()

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

    # extract X and Y values
    if 'X' in line:
        X = float(re.findall(r"X([\d\.-]+)", line)[0])
        Y = float(re.findall(r"Y([\d\.-]+)", line)[0])

        X_new = (X - X_initial) * math.cos(rotation_theta) - (Y - Y_initial) * math.sin(rotation_theta) + X_initial + d_X
        Y_new = (X - X_initial) * math.sin(rotation_theta) + (Y - Y_initial) * math.cos(rotation_theta) + Y_initial + d_Y

        line = re.sub(r'X[\d\.-]+', f'X{X_new:.3f}', line)
        line = re.sub(r'Y[\d\.-]+', f'Y{Y_new:.3f}', line)

    # check if contains I and J values
    if re.search(r'I([\d\.-])+(\s+J([\d\.-]+))?', line):
        i=i+1
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

        r = math.sqrt((X_centre_old - X_start_old)**2 + (Y_centre_old - Y_start_old)**2) / 2
        k = -(X_new - X_start_new)/(Y_new - Y_start_new)
        X_m = (X_new + X_start_new) / 2
        Y_m = (Y_new + Y_start_new) / 2

        #calculate new centre
        x, y = symbols('x y')
        eq1 = (y - Y_m) / (x - X_m) - k
        eq2 = sqrt((x - X_new)**2 + (y - Y_new)**2) / 2 - r
        sol = solve((eq1, eq2), (x, y))

        # 输出解
        #print(i)
        #print(f"x = {sol[0]}, y = {sol[1]}")

        X_centre_new_1, X_centre_new_2 = sol[0]
        Y_centre_new_1, Y_centre_new_2 = sol[1]
        #print(X_centre_new_1,Y_centre_new_1)


        if -math.pi <= rotation_theta <= 0:
            if I <= 0 and J <= 0 : # Quadrant I
                if X_centre_new_1 - X_start_new <= 0 and Y_centre_new_1 - Y_start_new >= 0:
                    I_new = X_centre_new_1 - X_start_new
                    J_new = Y_centre_new_1 - Y_start_new
                else:
                    I_new = X_centre_new_2 - X_start_new
                    J_new = Y_centre_new_2 - Y_start_new

            if I >= 0 and J <= 0:  # Quadrant II
                if X_centre_new_1 - X_start_new <= 0 and Y_centre_new_1 - Y_start_new <= 0:
                    I_new = X_centre_new_1 - X_start_new
                    J_new = Y_centre_new_1 - Y_start_new
                else:
                    I_new = X_centre_new_2 - X_start_new
                    J_new = Y_centre_new_2 - Y_start_new

            if I >= 0 and J >= 0:  # Quadrant III
                if X_centre_new_1 - X_start_new >= 0 and Y_centre_new_1 - Y_start_new <= 0:
                    I_new = X_centre_new_1 - X_start_new
                    J_new = Y_centre_new_1 - Y_start_new
                else:
                    I_new = X_centre_new_2 - X_start_new
                    J_new = Y_centre_new_2 - Y_start_new

            if I <= 0 and J >= 0:  # Quadrant IV
                if X_centre_new_1 - X_start_new >= 0 and Y_centre_new_1 - Y_start_new >= 0:
                    I_new = X_centre_new_1 - X_start_new
                    J_new = Y_centre_new_1 - Y_start_new
                else:
                    I_new = X_centre_new_2 - X_start_new
                    J_new = Y_centre_new_2 - Y_start_new

        if 0 <= rotation_theta <= math.pi:
            if I <= 0 and J <= 0:  # Quadrant I
                if X_centre_new_1 - X_start_new >= 0 and Y_centre_new_1 - Y_start_new <= 0:
                    I_new = X_centre_new_1 - X_start_new
                    J_new = Y_centre_new_1 - Y_start_new
                else:
                    I_new = X_centre_new_2 - X_start_new
                    J_new = Y_centre_new_2 - Y_start_new

            if I >= 0 and J <= 0:  # Quadrant II
                if X_centre_new_1 - X_start_new >= 0 and Y_centre_new_1 - Y_start_new >= 0:
                    I_new = X_centre_new_1 - X_start_new
                    J_new = Y_centre_new_1 - Y_start_new
                else:
                    I_new = X_centre_new_2 - X_start_new
                    J_new = Y_centre_new_2 - Y_start_new

            if I >= 0 and J >= 0:  # Quadrant III
                if X_centre_new_1 - X_start_new <= 0 and Y_centre_new_1 - Y_start_new >= 0:
                    I_new = X_centre_new_1 - X_start_new
                    J_new = Y_centre_new_1 - Y_start_new
                else:
                    I_new = X_centre_new_2 - X_start_new
                    J_new = Y_centre_new_2 - Y_start_new

            if I <= 0 and J >= 0:  # Quadrant IV
                if X_centre_new_1 - X_start_new <= 0 and Y_centre_new_1 - Y_start_new <= 0:
                    I_new = X_centre_new_1 - X_start_new
                    J_new = Y_centre_new_1 - Y_start_new
                else:
                    I_new = X_centre_new_2 - X_start_new
                    J_new = Y_centre_new_2 - Y_start_new

        #print(X_start_new,Y_start_new)

        line = re.sub(r'I[\d\.-]+', f'I{I_new:.3f}', line)
        line = re.sub(r'J[\d\.-]+', f'J{J_new:.3f}', line)
        #print(i,f'Yc_old{X_centre_old} Y_old{Y_centre_old} X_new{X_centre_new} Y_new{Y_centre_new}')

    #adaption of new spindle_speed and feed_rate
    if 'S' in line:
        line = re.sub(r'S[\d\.-]+', f'S{spindle_speed:.3f}', line)

    if 'F' in line:
        line = re.sub(r'F[\d\.-]+', f'F{feed_rate:.3f}', line)

    # add this line to new G code
    new_Gcode.append(line)

#new_line = "G94 F{}\nM03 S{}\n".format(feed_rate, spindle_speed)
#line = list(line)
#line.insert(4, new_line)
#line = ''.join(line)

#print(''.join(new_Gcode))
file_path_transformed = save_transformed_file(file_path_completed)
with open(file_path_transformed, "w") as f:
    f.write(''.join(new_Gcode))


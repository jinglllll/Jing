import numpy as np
import re
import math
import xlwt
import pandas as pd
from tkinter import *
from tkinter import messagebox

"""
#set up input box
def getInput(title, message):
    def return_callback(event):
        print('quit...')
        root.quit()

    def close_callback():
        messagebox.showinfo('message', 'no click...')

    root = Tk(className=title)
    root.wm_attributes('-topmost', 1)
    screenwidth, screenheight = root.maxsize()
    width = 300
    height = 100
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(size)
    root.resizable(0, 0)
    lable = Label(root, height=2)
    lable['text'] = message
    lable.pack()
    entry = Entry(root)
    entry.bind('<Return>', return_callback)
    entry.pack()
    entry.focus_set()
    root.protocol("WM_DELETE_WINDOW", close_callback)
    root.mainloop()
    str = entry.get()
    root.destroy()
    return str

#get the position users want
input_X = float(getInput('Input Dialog', 'Please enter X:'))
input_Y = float(getInput('Input Dialog', 'Please enter Y:'))
#input_Z = float(getInput('Input Dialog', 'Please enter Z'))
input_Rotation = float(getInput('Input Dialog', 'Please enter Rotation Angle:'))

#set spindle speed and feed rate
feed_rate = float(getInput('Input Dialog', 'Please enter feed rate:'))
spindle_speed = float(getInput('Input Dialog', 'Please enter spindle speed:'))
"""
input_Rotation = 45
input_X = 1
input_Y = 1

#the initial fixed position
initial_position = [0,0]
X_initial = initial_position[0]
Y_initial = initial_position[1]
#d_X = (input_X - X_initial)
#d_Y = (input_Y - Y_initial)
d_X = (input_X - X_initial)*50
d_Y = (input_Y - Y_initial)*50
#trans_vector = np.array([1, 2])
#d_X = trans_vector[0]
#d_Y = trans_vector[1]
#i=0



# define the transformation parameters
rotation_theta = -input_Rotation * math.pi/180
X_Rotationcentre = (input_X + 1.5) * 50
Y_Rotationcentre = (input_Y + 1.5) * 50

r = 55 #distance between initial point of workpiece to the rotation centre
a = math.sqrt(r**2 + 1125)
alpha = rotation_theta + math.atan(r / (75*math.sqrt(2)))

"""
col1 = "feed_rate"
col2 = "spindle_speed"
col3 = "input_X"
col4 = "input_Y"
col5 = "rotation"
data = pd.DataFrame({col1: feed_rate, col2: spindle_speed, col3: input_X, col4: input_Y, col5: input_Rotation}, index=[0])
data.to_excel('state.xlsx')
"""

#complete XY in each line
with open('D:\\Gcode_tool20mm.txt', 'r') as f:
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

with open("D:\\Gcode_tool20mm_1.txt", "w") as f:
    f.write(''.join(Gcode))

# read the new file
with open('D:\\Gcode_tool20mm_1.txt', 'r') as f:
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

        cot_alpha = 1 / math.tan(alpha)

        X_new = (X - X_Rotationcentre) * math.cos(rotation_theta) - (Y - Y_Rotationcentre) * math.sin(rotation_theta)\
                + X_Rotationcentre + d_X + input_X + a * cot_alpha
        Y_new = (X - X_Rotationcentre) * math.sin(rotation_theta) + (Y - Y_Rotationcentre) * math.cos(rotation_theta)\
                + Y_Rotationcentre + d_Y + input_Y + a * math.tan(alpha)

        line = re.sub(r'X[\d\.-]+', f'X{X_new:.3f}', line)
        line = re.sub(r'Y[\d\.-]+', f'Y{Y_new:.3f}', line)

    #if 'Z' in line:
    #    Z = float(re.findall(r"Z([\d\.-]+)", line)[0])
    #    Z_new = Z + input_Z
    #    line = re.sub(r'Z[\d\.-]+', f'X{Z_new:.3f}', line)

    # check if contains I and J values
    if re.search(r'I([\d\.-])+(\s+J([\d\.-]+))?', line):
        #i=i+1
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

        X_centre_new = (X_centre_old - X_Rotationcentre) * math.cos(rotation_theta) - (Y_centre_old - Y_Rotationcentre) \
                       * math.sin(rotation_theta) + X_Rotationcentre + d_X + input_X + a * cot_alpha
        Y_centre_new = (X_centre_old - X_Rotationcentre) * math.sin(rotation_theta) + (Y_centre_old - Y_Rotationcentre) \
                       * math.cos(rotation_theta) + Y_Rotationcentre + d_Y + input_Y + a * math.tan(alpha)

        I_new = X_centre_new - X_start_new
        J_new = Y_centre_new - Y_start_new
        #print(X_start_new,Y_start_new)

        line = re.sub(r'I[\d\.-]+', f'I{I_new:.3f}', line)
        line = re.sub(r'J[\d\.-]+', f'J{J_new:.3f}', line)
        #print(i,f'X_old{X_centre_old} Y_old{Y_centre_old} X_new{X_centre_new} Y_new{Y_centre_new}')

    """
    #adaption of new spindle_speed and feed_rate
    if 'S' in line:
        line = re.sub(r'S[\d\.-]+', f'S{spindle_speed:.3f}', line)

    if 'F' in line:
        line = re.sub(r'F[\d\.-]+', f'F{feed_rate:.3f}', line)
"""
    # add this line to new G code
    new_Gcode.append(line)

#new_line = "G94 F{}\nM03 S{}\n".format(feed_rate, spindle_speed)
#line = list(line)
#line.insert(4, new_line)
#line = ''.join(line)

#print(''.join(new_Gcode))
with open("D:\\Gcode_tool20mm_2.txt", "w") as f:
    f.write(''.join(new_Gcode))






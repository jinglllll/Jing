with open('D:\\11karl\\Masterarbeit\\NX model\\Gcode_tool20mm_1.txt', 'r') as f:
    data1 = f.readlines()

#read the initial spindlespeed and feedrate
for line in data1:
    if 'S' in line:
        spindlespeed = float(re.findall(r"S([\d\.-]+)", line)[0])

    if 'F' in line:
        feedrate = float(re.findall(r"F([\d\.-]+)", line)[0])

#example fitnessfunction
def Fitnessfunction(a, b, c, d, e, spindlespeed, feedrate):
    f = a * X + b * Y + c * spindlespeed + d * feedrate + e * rotation_angle
    return f

#get the spindlespeed which minimize the fitnessfunction
def getNewSpindlespeed(spindlespeed, score, new_score):
    if score > new_score:
        new_spindlespeed = spindlespeed
        with open('D:\\11karl\\Masterarbeit\\NX model\\Gcode_tool20mm_1.txt', 'r') as f:
            data2 = f.readlines()

        for line in data2:
            if 'S' in line:
                line = re.sub(r'S[\d\.-]+', f'S{new_spindlespeed:.3f}', line)

    return new_spindlespeed

#get the feedrate which minimize the fitnessfunction
def getNewFeedrate(feedrate, score, new_score):
    if score > new_score:
        new_feedrate = feedrate
        with open('D:\\11karl\\Masterarbeit\\NX model\\Gcode_tool20mm_1.txt', 'r') as f:
            data2 = f.readlines()

        for line in data2:
            if 'F' in line:
                line = re.sub(r'S[\d\.-]+', f'S{new_feedrate:.3f}', line)
    return new_feedrate

#here is a simple example optimization proccess
score = None
total_episode = 1000
f = {} #define library
a, b, c, d, e = 1, 2, 3, 4, 5
for i in range(total_episode):

    f[f'{i}, (S={spindlespeed}, F={feedrate})'] = score #store the state
    new_score = float(Fitnessfunction(a, b, c, d, e, spindlespeed, feedrate))

    if score is None:
        score = new_score
        continue

    new_spindlespeed = getNewSpindlespeed(spindlespeed, score, new_score)
    new_feesrate = getNewFeedrate(feedrate, new_score, score)

    spindlespeed = new_spindlespeed
    feedrate = new_feesrate


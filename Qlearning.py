from ctypes import *

mydll = WinDLL('kernel32')
#print(mydll.timeGetTime())

# from vrepEnv import ArmEnv
import b0RemoteApi
# noinspection PyUnresolvedReferences
import sys
import os
# noinspection PyUnresolvedReferences
import itertools
import random
import matplotlib.pyplot as plt
import numpy as np
# noinspection PyUnresolvedReferences
import pandas as pd
from datetime import datetime
# noinspection PyUnresolvedReferences
import gym

now = datetime.now()

current_time_1 = now.strftime("%H:%M:%S")
current_time = current_time_1.replace(":", ".")

global actionSpace

actionSpace = ["t", "rP", "rH", "rC", "mC", "pB", "i_A"]

filepathForResults_2 = os.getcwd() + "/resultsRandomSearch/" + current_time
filepathForResults = filepathForResults_2.replace("\\", "/")
if not os.path.exists(filepathForResults):
    os.makedirs(filepathForResults)
print("Results will be saved to: " + filepathForResults)


def checkPreconditions(action, stateVector):
    """ this function evaluates the action preconditions from Table II in the paper."""

    s_area = stateVector[0]
    s_parts = stateVector[1]
    s_robot = stateVector[2]
    s_gear = stateVector[3]
    s_rH = stateVector[4]
    s_rC = stateVector[5]
    s_cover = stateVector[6]

    if action == "i_A":
        return True  # reset always possible
    if action == "t":
        return True  # transition always possible
    elif action == "rP":
        return not stateVector[0]  # not s_area
    elif action == "rH":
        return s_area and (not s_cover) and (not s_gear)
    elif action == "rC":
        return s_area and (not s_cover)
    elif action == "mC":
        return s_area and (not s_cover)
    elif action == "pB":
        return s_area
    else:
        raise Exception("Error in function 'checkPreconditions': argument is not a valid action")  # 引发异常


def getFeasibleActions(stateVector):
    feasibleActions = list()  # list() 方法用于将元组转换为列表。元组与列表是非常类似的，区别在于元组的元素值不能修改，元组是放在括号中，列表是放于方括号中。
    for action in actionSpace:
        if checkPreconditions(action, stateVector):
            feasibleActions.append(action)
    return feasibleActions


def changeStateToString(state): ##
    stateString_str = ''
    for item in state:
        if item is True:
            stateString_str += '1'
        else:
            stateString_str += '0'
    return stateString_str

initialEpsilon = 0.8  # starting value of epsilon
finalEpsilon = 0.01  # final value of epsilon
maxEpsilon = 2000
epsilon = initialEpsilon

class Q_Table: ##
    def __init__(self, action_space):
        self.actions = action_space
        self.q_table = pd.DataFrame(columns=action_space, dtype=np.float64)
        self.epsilon = 0.8

    def checkStateExist(self, state):
        if state not in self.q_table.index:
            self.q_table = self.q_table.append(
                pd.Series(
                    [0] * len(self.actions),
                    index=self.q_table.columns,
                    name=state,
                )
            )

    def getMaxAction(self, stateString, feasible_actions):
        self.checkStateExist(stateString)
        actionList = feasible_actions
        maxAction = actionList[0]
        maxValue = self.q_table.loc[stateString, maxAction]
        for item in actionList:
            itemValue = self.q_table.loc[stateString, item]
            if itemValue > maxValue:
                maxAction = item
                maxValue = itemValue
        return maxAction

    def chooseAction(self, stateString, feasible_actions):
        self.checkStateExist(stateString)
        actionList = feasible_actions
        if np.random.rand() < self.epsilon:
            action = self.getMaxAction(stateString, feasible_actions)
            self.epsilon -= (finalEpsilon - initialEpsilon) / maxEpsilon
        else:
            # # 选择随机行为
            action = np.random.choice(actionList)
        return action


agent_q = Q_Table(actionSpace)


def getMaxRiskValues(risksFromAllEpisodes):
    maxRiskList = list()
    for riskSequence in risksFromAllEpisodes:
        if len(riskSequence) == 0:
            maxRiskList.append(0)  # append 附加在列表最后一个新的值
        else:
            maxRiskList.append(max(riskSequence))
    return maxRiskList


def convertToPaddedArray(inputList, typeOfArray):  # PaddedArray填补的阵列
    # convert nested嵌套的 list of different length to numpy array (padded with zeros for uniform dimensions)
    if typeOfArray == "float":
        paddedArray = np.zeros([len(inputList), len(max(inputList, key=lambda x: len(x)))])
        # 返回几行几列的数组
        # 取所有数值里面，第len(x)维度数值最大的那一组数字
    # elif typeOfArray == "string":
    else:
        paddedArray = np.chararray([len(inputList), len(max(inputList, key=lambda x: len(x)))])
    for i, j in enumerate(inputList):
        paddedArray[i][0:len(j)] = j
    return paddedArray


with b0RemoteApi.RemoteApiClient('b0RemoteApi_V-REP',
                                 'b0RemoteApi') as client:  # This line defines the client, which provides all functions of the remote API
    # the function list can be found here: https://www.coppeliarobotics.com/helpFiles/en/b0RemoteApi-functionList.htm

    actionIsSet = False
    N_STEPS_EPISODE = 10  # max episode length (shorter episodes are possible if reset action i_A is sampled)
    N_STEPS_TOTAL = 10000
    lr = 0.2
    gamma = 0.99
    # initialize simulation
    client.simxSynchronous(True)
    client.simxStartSimulation(client.simxServiceCall())  # use client to start the simulation
    client.simxSynchronousTrigger()

    stepCounterTotal = 0
    stepCounterEpisode = 0
    episodeCounter = 1
    risksFromAllEpisodes = list()  # list of risk values over the whole search 创建了一个空列表
    actionsFromAllEpisodes = list()  # list of action sequences from all episodes
    motionParametersFromAllEpsiodes = list()

    motionParametersMin = [-0.2, 0.8, 1]
    motionParametersMax = [0.2, 1.2, 1.5]
    motionParametersNominal = [0, 1, 1]

    # main loop (1 execution = 1 search episode)
    while (stepCounterTotal <= N_STEPS_TOTAL):
        # reset = False
        # initialize new episode

        print("-------------- new episode " + str(episodeCounter) + " --------------")
        reset = False
        episodeCounter += 1
        risksFromThisEpisode = list()
        actionsFromThisEpisode = list()
        motionParametersFromThisEpsiode = list()
        stepCounterEpisode = 0
        client.simxCallScriptFunction("resetMaxRisk@RiskMetricCalculator", "sim.scripttype_childscript", 1,
                                      client.simxServiceCall())
        client.simxCallScriptFunction("reset@Bill", "sim.scripttype_childscript", 1, client.simxServiceCall())

        # action loop (1 execution = 1 single action in the simulation)
        while (stepCounterEpisode <= N_STEPS_EPISODE) and not reset:

            # check if human model is cucrently performaing an action
            _,isRunning = client.simxCallScriptFunction("isHumanModelActive@Bill","sim.scripttype_childscript",1,client.simxServiceCall())

            if isRunning:
                # step simulation forward
                client.simxSynchronousTrigger()
            else:
                if not (stepCounterEpisode == 0):
                    print("action "+str(stepCounterEpisode))
                    # retrieve maximum risk value from previous action
                    _,risk = client.simxCallScriptFunction("getMaxRisk@RiskMetricCalculator","sim.scripttype_childscript",1,client.simxServiceCall())
                    client.simxCallScriptFunction("resetMaxRisk@RiskMetricCalculator","sim.scripttype_childscript",1,client.simxServiceCall())
                    risksFromThisEpisode.append(risk)
                    print("risk from this action: "+str(risk))

                # sample  action
                currentState = client.simxCallScriptFunction("getStateVector@StateVariablesTracker",
                                                             "sim.scripttype_childscript", None,
                                                             client.simxServiceCall())

                currentStateFeasibleActions = getFeasibleActions(currentState)
                stateString = changeStateToString(currentState)
                action = agent_q.chooseAction(stateString, currentStateFeasibleActions)

                client.simxCallScriptFunction("setAction@Bill", "sim.scripttype_childscript", action,
                                              client.simxServiceCall())

                print("new action:" + action)

                _, risk = client.simxCallScriptFunction("getMaxRisk@RiskMetricCalculator", "sim.scripttype_childscript", 1,
                                                        client.simxServiceCall())
                client.simxCallScriptFunction("resetMaxRisk@RiskMetricCalculator", "sim.scripttype_childscript", 1,
                                              client.simxServiceCall())
                risksFromThisEpisode.append(risk)

                nextState = client.simxCallScriptFunction("getStateVector@StateVariablesTracker",
                                                           "sim.scripttype_childscript", None, client.simxServiceCall())

                reward = float(risk)
                nextStateString = changeStateToString(nextState)
                nextStateFeasibleAction = getFeasibleActions(nextState)
                QPredict = agent_q.q_table.loc[stateString, action]
                nextAction = agent_q.getMaxAction(nextStateString, nextStateFeasibleAction)


                QTarget = reward + gamma * agent_q.q_table.loc[nextStateString, nextAction]

                agent_q.q_table.loc[stateString, action] = (1 - lr) * QPredict + lr * (QTarget - QPredict)
                currentState = nextState

                stepCounterEpisode += 1
                stepCounterTotal += 1

        # save data from this episode
        if (not stepCounterTotal == 0):  # don't do this in the first epsiode, since there are no risk values available
            risksFromAllEpisodes.append(risksFromThisEpisode)
            actionsFromAllEpisodes.append(actionsFromThisEpisode)
            motionParametersFromAllEpsiodes.append(motionParametersFromThisEpsiode)
        print(risksFromAllEpisodes)

    # save and plot results
    # action sequences
    with open(filepathForResults + '/actionSequences.txt', 'w') as filehandle:
        filehandle.writelines("%s\n" % place for place in actionsFromAllEpisodes)
    # risk values
    results_risk = convertToPaddedArray(risksFromAllEpisodes, "float")
    np.save(filepathForResults + "/risks.npy", results_risk)

    maxRiskList = getMaxRiskValues(risksFromAllEpisodes)
    plt.plot(maxRiskList, "*")
    plt.ylabel('Max risk of episode')
    plt.xlabel('Episodes')
    plt.grid(True)
    plt.show()
    # plt.save(filepathForResults+str("figure.png")
    print(agent_q.q_table)

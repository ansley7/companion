# import sys
# is_py2 = sys.version[0] == '2'
# if is_py2:
#     import Queue as queue
# else:
#     import queue as qu
import queue as qu
import threading as th
import multiprocessing as mp
import time

from flask import Flask, render_template
from flask_ask import Ask, statement, question

import cvtest
# import LegoTracker


# this file calls all others as threads then moves data from queue


app = Flask(__name__)
ask = Ask(app, '/')

cvQueue = mp.JoinableQueue()

allQueues = []
allQueues.append(cvQueue)


@app.route('/')
def hello_world():
	return "Flask Server is Online!"

@ask.launch
def launched():
	return question("hello. what would you like me to do?").reprompt(
		"if you don't need me, please put me to sleep.")


@ask.intent('AMAZON.FallbackIntent')
def default():
	return question("Sorry, I don't understand that command. What would you like me to do?").reprompt(
		"What would you like me to do now?")

@ask.intent('SleepIntent')
def sleep():
	return statement('goodnight')

@ask.intent('terminate')
def terminate():
    for queue in allQueues:
        queue.put("terminate")
    return statement('processes are terminated')

@ask.intent('testComunication')
def testComunications():
	return statement('Jetson Backend is opperational. If it was not	I would not be alive')

@ask.intent('LegoTracker')
def trackMe():
    cvQueue.put("pickupLegos")
    cvQueue.join()
    return statement('Right away')

@ask.intent('stopActing')
def stopActing():
    cvQueue.put("halt")
    cvQueue.join()
    return statement('Ok. Fine! I don\'t like you anyways')


if __name__ == '__main__':
    alexaTh = th.Thread(target= app.run)
    alexaTh.daemon = True
    cvTh = mp.Process(target= openCVController.run, args= (cvQueue, ))

    allThreads = []
    allThreads.append(cvTh)

    alexaTh.start()

    for thread in allThreads:
        thread.start()

    for thread in allThreads:
        thread.join()
    
    print("exiting")
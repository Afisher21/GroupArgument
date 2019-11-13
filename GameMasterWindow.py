#!python3

import tkinter as tk
from tkinter import ttk as ttk
from Classes import *
from dotmap import DotMap

g_question = "Name a chore that people put off because they have work the next day:"
g_answers = [SurveyAnswer("Take out trash",35), SurveyAnswer("Dishes",30), SurveyAnswer("Vacuum",18), SurveyAnswer("Laundry",6), SurveyAnswer("Clean bathroom",4), SurveyAnswer("Dust",3)]
g_contestants = ["BASE","DEP","ES","ENS","STACK","SIGMA"]   

master = tk.Tk()
# Populate the question that contestants are working with
quest = tk.Label(master, text=g_question, font=("Times",15)).grid(row=1, columnspan=10)
# Populate the survey answers so that Game Master knows which ones are available
for resp in range(len(g_answers)):
    tk.Label(master, text=g_answers[resp].count).grid(column=0,row=2+resp)
    tk.Label(master, text=g_answers[resp].response).grid(column=1,row=2+resp)

# Populate the playerbase
for cont in range(len(g_contestants)):
    playerCol = 2 + cont
    tk.Label(master, text=g_contestants[cont]).grid(column=playerCol, row=0)
    for resp in range(len(g_answers)):
        chk = ttk.Checkbutton(master)
        chk.state(['!alternate'])
        chk.state(['!selected'])
        chk.grid(column=playerCol,row = 2+resp)
    # Add score box for this player
    tk.Label(master, text="0").grid(column=playerCol, row=len(g_answers) + 2)

tk.Label(master, text="(SUBMIT)").grid(column= 3 + len(g_contestants), row = 0)
# Defines the Callback for when a "submit" button is pressed. Adds the points to the players score
def Submit(row):
    questionScoreBox = master.grid_slaves(row, 0)
    questionScore = int(questionScoreBox[0]['text'])
    for col in range(len(g_contestants)):
        contestant = col + 2
        chkbox = master.grid_slaves(row, contestant)
        if(chkbox[0].state()):
            print("Contestant " + str(contestant) + " Should gain " + str(questionScore) + " points")
            scorebox = master.grid_slaves(len(g_answers) + 2, contestant)
            oldscore = int(scorebox[0]['text'])
            newScore = oldscore + questionScore
            print("New score: " + str(newScore))
            scorebox[0]['text'] = str(newScore)
        chkbox[0].state(['disabled'])
        
# Add submit buttons. These are used when a contestant says a response that's already on the board
for resp in range(len(g_answers)):
    rw = resp + 2
    but = tk.Button(master, text="Submit scoring")
    but['command'] = lambda rw=rw: Submit(rw)
    but.grid(column= 3 + len(g_contestants), row=rw)

tk.mainloop()
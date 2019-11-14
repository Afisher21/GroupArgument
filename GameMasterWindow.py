#!python3
import tkinter as tk
from tkinter import ttk as ttk
from Classes import *
from dotmap import DotMap

def main(**kwargs):
    questionParam = 'question'
    answerParam = 'answers'
    playerParam = 'contestants'
    if questionParam in kwargs and answerParam in kwargs and kwargs[questionParam] is not None and kwargs[answerParam] is not None:
        g_question = kwargs[questionParam]
        g_answers = kwargs[answerParam]
    else:
        g_question = random.choice(list(db.keys()))
        g_answers = db[g_question]
    if playerParam in kwargs and kwargs[playerParam] is not None:
        g_contestants = kwargs[playerParam]
    else:
        g_contestants = ['Family 1', 'Family 2']
    print('Prompt: ' + g_question)
    print('Responses: ' + str(g_answers))
    print('Players: ' + str(g_contestants))
    
    # Offset table to avoid magic numbers
    offsets = DotMap()
    offsets.SubmitButton = 2 + len(g_contestants)
    offsets.DisplayCount = 0
    offsets.DisplayAnswer = 1

    master = tk.Tk()
    # Populate the question that contestants are working with
    quest = tk.Label(master, text=g_question, font=("Times",15)).grid(row=1, columnspan=10)
    # Populate the survey answers so that Game Master knows which ones are available
    for resp in range(len(g_answers)):
        tk.Label(master, text=g_answers[resp][1]).grid(column=0,row=2+resp)
        tk.Label(master, text=g_answers[resp][0]).grid(column=1,row=2+resp)

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
            # Disable check boxes
            chkbox[0].state(['disabled'])
        # Disable "Submit score" button
        submitBut = master.grid_slaves(row, len(g_contestants) + 3)
        submitBut[0]['state'] = 'disabled'
            
    # Add submit buttons. These are used when a contestant says a response that's already on the board
    for resp in range(len(g_answers)):
        rw = resp + 2
        but = tk.Button(master, text="Submit scoring")
        but['command'] = lambda rw=rw: Submit(rw)
        but.grid(column= 3 + len(g_contestants), row=rw)

    tk.mainloop()

if __name__ == "__main__":
    # Argparse and sys are for CLI arguments
    # random and DataBase are for default parameters
    import argparse, sys, random
    from DataBase import db
    if sys.version_info.minor > 7 and sys.version_info.major >= 3:
        act = 'extend'
    else:
        act = 'append'
    parser = argparse.ArgumentParser(
        description='Create the GameMaster window for playing GroupArgument')
    parser.add_argument('-c', '--contestants',
        action=act,
        help='Names of contestants to play.')
    parser.add_argument('-f', '--find',
        help='Find a particular Survey Question. Provide as much of the prompt as you can, and we will regex for a match')
    parser.add_argument('-ns','--newsurvey',
        help='Specify your own survey question to the commandline. Only valid with "nr" specified as well. This will be the question used')
    parser.add_argument('-nr','--newresults',
        action=act,
        help='Specify your own survey responses to the commandline. Only valid if "ns" specified. Should take the form of "(Answer,ResponseCount)"')
        
    ns = parser.parse_args(sys.argv[1:])
    params = {}
    # Handle contestants
    if ns.contestants is not None:
        if act is 'append':
            # Workaround to allow extend like behavior on 3.7
            contestants = (','.join(ns.contestants)).split(',')
        else:
            contestants = ns.contestants
        params['contestants'] = contestants
    # Handle q/a logic
    if ns.find is not None:
        print('NotImplementedError')
        raise NotImplementedError
    if ns.newsurvey is None or ns.newresults is None:
        params['question'] = ns.newsurvey
        params['answers'] = ns.newresults
    print("Arguments passed to main: " + str(params))
    main(**params)
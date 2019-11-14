#!python3
import tkinter as tk
from Classes import *
from dotmap import DotMap

def ValidateWindowArgs(**kwargs):
    if 'master' not in kwargs or kwargs['master'] is None:
        raise Exception("'master' tk window not provided for adding objects to!")
    if 'contestants' not in kwargs or kwargs['contestants'] is None or len(kwargs['contestants']) < 2:
        raise Exception("'contestantss' is invalid! Please provide a list of at least 2 names for a valid game.")
    if 'question' not in kwargs or kwargs['question'] is None or kwargs['question'] is '':
        raise Exception("'question' is invalid! Please provide a question for the contestants to respond to.")
    if 'answers' not in kwargs or kwargs['answers'] is None or len(kwargs['answers']) < 1:
        raise Exception("'answers' is invalid! Please provide the expected survey results so contestants can have something to be scored against.")
    if 'offsets' not in kwargs or kwargs['offsets'] is None:
        raise Exception("'offsets' is invalid! Please provide an offset table for where to draw the various elements. See 'main' function for example")
    offsets = kwargs['offsets']
    if (
            'DisplayCount' not in offsets or
            'DisplayAnswer' not in offsets or
            'PlayerStart' not in offsets or
            'PlayerEnd' not in offsets or
            'SubmitButton' not in offsets or
            'RoundMultiplier' not in offsets or
            'Question' not in offsets or 
            'Names' not in offsets or
            'AnswerBegin' not in offsets or
            'AnswerEnd' not in offsets or
            'PlayerScore' not in offsets
        ):
        raise Exception("'offsets' is invalid! Missing one or more offset specifications. Please examine 'main' for full definition")

def PopulatePlayers(**kwargs):
    from tkinter import ttk as ttk
    for cont in range(len(kwargs['contestants'])):
        playerCol = kwargs['offsets'].PlayerStart + cont
        tk.Label(kwargs['master'], text=kwargs['contestants'][cont]).grid(column=playerCol, row=kwargs['offsets'].Names)
        for resp in range(len(kwargs['answers'])):
            # Create checkbox , set to empty as default
            chk = ttk.Checkbutton(kwargs['master'])
            chk.state(['!alternate'])
            chk.state(['!selected'])
            chk.grid(column=playerCol,row = kwargs['offsets'].AnswerBegin + resp)
        # Add score box for this player
        tk.Label(kwargs['master'], text="0").grid(column=playerCol, row = kwargs['offsets'].PlayerScore)

def PopulateSubmitButtons(**kwargs):
    # Defines the Callback for when a "submit" button is pressed. Adds the points to the players score
    # Side note on useage - .grid_slaves returns a list of all matching values
    #  BugBug: Area of improvement would be to have a singular call to get row, and then parse through that
    def Submit(row):
        questionScoreBox = kwargs['master'].grid_slaves(row, kwargs['offsets'].DisplayCount)
        questionScore = int(questionScoreBox[0]['text'])
        answerProvided = False
        for col in range(len(kwargs['contestants'])):
            contestant = col + kwargs['offsets'].PlayerStart
            chkbox = kwargs['master'].grid_slaves(row, contestant)
            if(chkbox[0].state()):
                answerProvided = True
                scorebox = kwargs['master'].grid_slaves(kwargs['offsets'].PlayerScore, contestant)
                oldscore = int(scorebox[0]['text'])
                newScore = oldscore + questionScore
                scorebox[0]['text'] = str(newScore)
            # Disable check boxes
            chkbox[0].state(['disabled'])
        # Avoid accidental button presses disabling button
        if answerProvided is not True:
            for col in range(len(kwargs['contestants'])):
                contestant = col + kwargs['offsets'].PlayerStart
                chkbox = kwargs['master'].grid_slaves(row, contestant)
                chkbox[0].state(['!disabled'])
        else:
            # Also Disable "Submit score" button
            submitBut = kwargs['master'].grid_slaves(row, kwargs['offsets'].SubmitButton)
            submitBut[0]['state'] = 'disabled'
            
    # Add submit buttons. These are used when a contestant says a response that's already on the board
    for resp in range(len(kwargs['answers'])):
        rw = resp + kwargs['offsets'].AnswerBegin
        but = tk.Button(kwargs['master'], text="Submit scoring")
        but['command'] = lambda rw=rw: Submit(rw)
        but.grid(column= kwargs['offsets'].SubmitButton, row=rw)


def PopulateWindow(**kwargs):
    # Validate/provide shorthand for args
    ValidateWindowArgs(**kwargs)
    master      =   kwargs['master']
    question    =   kwargs['question']
    contestants =   kwargs['contestants']
    answers     =   kwargs['answers']
    offsets     =   kwargs['offsets']
    
    # Populate the question that contestants are working with
    tk.Label(master, text=question, font=("Times",15)).grid(row=offsets.Question, columnspan=10)
    tk.Label(master, text="#").grid(row=offsets.Names, column = offsets.DisplayCount)
    tk.Label(master, text='response').grid(row = offsets.Names, column = offsets.DisplayAnswer)
    
    # Populate the survey answers so that Game Master knows which ones are available
    for resp in range(len(answers)):
        tk.Label(master, text=answers[resp][1]).grid(column=offsets.DisplayCount,row = offsets.AnswerBegin + resp)
        tk.Label(master, text=answers[resp][0]).grid(column=offsets.DisplayAnswer,row = offsets.AnswerBegin + resp)
        
     # Populate the playerbase
    PopulatePlayers(**kwargs)
    
    # Populate Submit fields
    tk.Label(master, text="(SUBMIT)").grid(column= offsets.SubmitButton, row = offsets.Names)
    PopulateSubmitButtons(**kwargs)
    

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
    # x offsets ( 0 == L, (max) == R)
    offsets.DisplayCount = 0
    offsets.DisplayAnswer = 1
    offsets.PlayerStart = 2
    offsets.PlayerEnd = offsets.PlayerStart + len(g_contestants) - 1
    offsets.SubmitButton = offsets.PlayerEnd + 1
    # y offsets (0 == Top, (max) == bototm)
    offsets.RoundMultiplier = 0
    offsets.Question = 1
    offsets.Names = 2
    offsets.AnswerBegin = 3
    offsets.AnswerEnd = offsets.AnswerBegin + len(g_answers) - 1
    offsets.PlayerScore = offsets.AnswerEnd + 1

    master = tk.Tk()
    PopulateWindow(master=master, offsets=offsets, question=g_question, answers=g_answers, contestants=g_contestants)
     
    def DISABLE(button):
        button["state"] = "disabled"
    
    if len(g_contestants) is 2:
        # Traditional FF! This means we should keep track of incorrect answers :)
        for i in range(3):
            but = tk.Button(master, text='Incorrect guess')
            but['command'] = lambda b=but: DISABLE(b)
            but.grid(column = offsets.SubmitButton + 1, row=offsets.AnswerBegin + 2*i, rowspan=2)

    but = tk.Button(master, text = 'Next Round')
    # but['command'] = lambda nextround()
    but.grid(columnspan=10, row = offsets.PlayerScore + 1)
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
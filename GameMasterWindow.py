#!python3
import tkinter as tk
from Classes import *
from dotmap import DotMap

g_RoundScore = 0
g_obj = {}

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

def PopulateAnswers(**kwargs):
    for resp in range(len(kwargs['answers'])):
        tk.Label(kwargs['master'], text=kwargs['answers'][resp][1]).grid(column=kwargs['offsets'].DisplayCount,row = kwargs['offsets'].AnswerBegin + resp)
        tk.Label(kwargs['master'], text=kwargs['answers'][resp][0]).grid(column=kwargs['offsets'].DisplayAnswer,row = kwargs['offsets'].AnswerBegin + resp)

def FindActivePlayer(**kwargs):
    if len(kwargs['contestants']) is not 2:
        raise Exception("FindActivePlayer is only valid when there are 2 players")
    p1 = kwargs['master'].grid_slaves(column = kwargs['offsets'].PlayerStart)
    for row in p1:
        if isinstance(row, tk.ttk.Checkbutton):
            if 'focus' in row.state():
                return kwargs['offsets'].PlayerStart
    p2 = kwargs['master'].grid_slaves(column = kwargs['offsets'].PlayerEnd)
    for row in p2:
        if isinstance(row, tk.ttk.Checkbutton):
            if 'focus' in row.state():
                return kwargs['offsets'].PlayerEnd
    return 0

def PopulateSubmitButtons(**kwargs):
    # Defines the Callback for when a "submit" button is pressed. Adds the points to the players score
    # Side note on useage - .grid_slaves returns a list of all matching values
    #  BugBug: Area of improvement would be to have a singular call to get row, and then parse through that
    def Submit(row):
        questionScoreBox = kwargs['master'].grid_slaves(row, kwargs['offsets'].DisplayCount)
        questionScore = int(questionScoreBox[0]['text']) * int(kwargs['round'])
        answerProvided = False
        for col in range(len(kwargs['contestants'])):
            contestant = col + kwargs['offsets'].PlayerStart
            chkbox = kwargs['master'].grid_slaves(row, contestant)
            # Award points to whichever team(s) submitted the associated answer
            if('selected' in chkbox[0].state()):
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
            # Keep track of score for 2 player game
            if len(kwargs['contestants']) is 2:
                global g_RoundScore
                g_RoundScore += questionScore
        # In 2 player games, only 1 player can score at a time.
        # Disable other player to avoid accidental point giving
        # BugBug: Could improve performance by only doing this once
        if len(kwargs['contestants']) is 2:
            inactiveplayer = None
            active = FindActivePlayer(**kwargs)
            if active is kwargs['offsets'].PlayerStart:
                inactiveplayer = kwargs['master'].grid_slaves(column = kwargs['offsets'].PlayerEnd)
            elif active is kwargs['offsets'].PlayerEnd:
                inactiveplayer = kwargs['master'].grid_slaves(column = kwargs['offsets'].PlayerStart) 
            if inactiveplayer is not None:
                for row in inactiveplayer:
                    if isinstance(row, tk.ttk.Checkbutton):
                        row.state(['disabled'])
            
    # Add submit buttons. These are used when a contestant says a response that's already on the board
    for resp in range(len(kwargs['answers'])):
        rw = resp + kwargs['offsets'].AnswerBegin
        but = tk.Button(kwargs['master'], text="Submit scoring")
        but['command'] = lambda rw=rw: Submit(rw)
        but.grid(column= kwargs['offsets'].SubmitButton, row=rw)
        

def PopulateGroupSwitch(**kwargs):
    incorrectGuessText = 'Incorrect guess'
    scoreSwapText = 'Round score stolen'
    def DISABLE(button):
        button["state"] = "disabled"
        butGrid = kwargs['master'].grid_slaves(column = kwargs['offsets'].SubmitButton + 1)
        active = False
        for but in butGrid:
            # only care about the 3 disabled buttons
            if but['text'] == incorrectGuessText and but['state'] == 'normal':
                active = True
        if not active:
            for but in butGrid:
                if but['text'] == scoreSwapText:
                    but['state'] = ['normal']
        
    def SWAP(button, score):
        button["state"] = "disabled"
        # Subtract round score from active player, add to inactive
        prevTeam = FindActivePlayer(**kwargs)
        newTeam = (kwargs['offsets'].PlayerStart if prevTeam is kwargs['offsets'].PlayerEnd else kwargs['offsets'].PlayerEnd)
        prevTeamScore = kwargs['master'].grid_slaves(row = kwargs['offsets'].PlayerScore, column = prevTeam)[0]
        prevTeamScore['text'] = int(prevTeamScore['text']) - g_RoundScore
        newTeamScore = kwargs['master'].grid_slaves(row = kwargs['offsets'].PlayerScore, column = newTeam)[0]
        newTeamScore['text'] = int(newTeamScore['text']) + g_RoundScore
        # Swap which player is active
        prevCol = kwargs['master'].grid_slaves(column = prevTeam)
        for row in prevCol:
            if isinstance(row, tk.ttk.Checkbutton):
                if 'disabled' not in row.state():
                    row.state(['disabled'])
        newCol = kwargs['master'].grid_slaves(column = newTeam)
        for iter in range(len(newCol)):
            if isinstance(newCol[iter], tk.ttk.Checkbutton):
                if 'disabled' in newCol[iter].state() and 'selected' not in prevCol[iter].state():
                    newCol[iter].state(['!disabled'])
        
    # Traditional FF! This means we should keep track of incorrect answers
    possibleIncorrects = 3
    for i in range(possibleIncorrects):
        but = tk.Button(kwargs['master'], text=incorrectGuessText)
        but['command'] = lambda b=but: DISABLE(b)
        but.grid(column = kwargs['offsets'].SubmitButton + 1, row = kwargs['offsets'].AnswerBegin + 2*i, rowspan=2)
    
    # Add "Score steal" button
    but = tk.Button(kwargs['master'], text = scoreSwapText)
    global g_RoundScore
    but['command'] = lambda b=but, s=g_RoundScore: SWAP(b,s)
    but['state'] = 'disabled'
    but.grid(column = kwargs['offsets'].SubmitButton + 1, row = kwargs['offsets'].AnswerBegin + 2*possibleIncorrects, rowspan=2)

def PopulateWindow(**kwargs):
    # Validate/provide shorthand for args
    ValidateWindowArgs(**kwargs)
    master      =   kwargs['master']
    question    =   kwargs['question']
    contestants =   kwargs['contestants']
    answers     =   kwargs['answers']
    offsets     =   kwargs['offsets']
    curRound    =   str(kwargs['round']) # Force str value
    
    # Populate the question that contestants are working with
    tk.Label(master, text=question, font=("Times",15)).grid(row=offsets.Question, columnspan=10)
    tk.Label(master, text="#").grid(row=offsets.Names, column = offsets.DisplayCount)
    tk.Label(master, text='response').grid(row = offsets.Names, column = offsets.DisplayAnswer)
    
    # Populate the survey answers so that Game Master knows which ones are available
    PopulateAnswers(**kwargs)
    
    # Populate the playerbase
    PopulatePlayers(**kwargs)
    
    # Populate Submit fields
    tk.Label(master, text="(SUBMIT)").grid(column= offsets.SubmitButton, row = offsets.Names)
    PopulateSubmitButtons(**kwargs)
    
    # Populate "Incorrect guess" and "Steal round score" buttons
    if len(contestants) is 2:
        PopulateGroupSwitch(**kwargs)
    
    def NEXT_ROUND():
        import re
        global g_RoundScore
        g_RoundScore = 0
        PLAYER_COUNT = 1 + g_obj['offsets'].PlayerEnd - g_obj['offsets'].PlayerStart
        if 'used' not in g_obj or g_obj['used'] is None:
            g_obj['used'] = []
        g_obj['used'] = g_obj['used'].append(g_obj['question'])
        g_obj['question'] = None
        g_obj['answers'] = None
        # Store round multiplier & score( has to be done first due to lack of persistence in g_obj )
        contestantScores = []
        multLabel = g_obj['master'].grid_slaves(row = g_obj['offsets'].RoundMultiplier, column = 0)[0]
        prevRound = int(re.findall('\d+', multLabel['text'])[0])
        g_obj['round'] = str(prevRound + 1)
        multLabel['text'] = "Round multiplier: " + g_obj['round']
        for i in range(PLAYER_COUNT):
            label = g_obj['master'].grid_slaves(row = g_obj['offsets'].PlayerScore, column = g_obj['offsets'].PlayerStart + i)[0]
            contestantScores.append(label['text'])
            label.destroy()
        # Get new round content
        newQ, newA = GetQuestionAndAnswers(**g_obj)
        print('Round: ' + g_obj['round'] + ' question; "' + newQ + '"\n\tResponses: ' + str(newA))
        # Clean up previous round answers and submit buttons
        for i in range(1 + g_obj['offsets'].AnswerEnd - g_obj['offsets'].AnswerBegin):
            aRow = g_obj['master'].grid_slaves( row = g_obj['offsets'].AnswerBegin + i)
            for j in range(len(aRow)):
                # grid_forget is the more common way to do this, but actually causes a memory leak as the object iself still exists
                #  But now it exists where it can't be indexed( since it's off the grid) and we can't do anything with it as a result
                if j >= g_obj['offsets'].PlayerStart and j <= g_obj['offsets'].SubmitButton:
                    aRow[j].destroy()
        # Update g_obj contents
        g_obj['answers'] = newA
        g_obj['offsets'].AnswerEnd = g_obj['offsets'].AnswerBegin + len(newA)
        g_obj['question'] = newQ
        nextBut = g_obj['master'].grid_slaves(row = g_obj['offsets'].PlayerScore + 1)[0]
        g_obj['offsets'].PlayerScore = g_obj['offsets'].AnswerEnd + 1
        g_obj['offsets'].RoundMultiplier = g_obj['offsets'].PlayerScore
        
        # Update static fields location & contents
        questLabel = g_obj['master'].grid_slaves(row = g_obj['offsets'].Question)[0]
        questLabel['text'] = newQ
        nextBut.grid(columnspan = 10, row = offsets.PlayerScore + 1)
        multLabel.grid(row = g_obj['offsets'].RoundMultiplier, column = 0)
        
        PopulateAnswers(**g_obj)
        PopulatePlayers(**g_obj)
        PopulateSubmitButtons(**g_obj)
        # restore value of scores
        for i in range(PLAYER_COUNT):
            label = g_obj['master'].grid_slaves(row = g_obj['offsets'].PlayerScore, column = g_obj['offsets'].PlayerStart + i)[0]
            label['text'] = contestantScores[i]
        
    roundLabel = tk.Label(master, text= 'Round multiplier: ' + curRound)
    roundLabel.grid(row = offsets.RoundMultiplier, column = 0)
    but = tk.Button(master, text = 'Next Round')
    but['command'] = lambda: NEXT_ROUND()
    but.grid(columnspan=10, row = offsets.PlayerScore + 1)
    g_obj = kwargs

def GetQuestionAndAnswers(**kwargs):
    questionParam = 'question'
    usedQuestionsParam = 'used'
    answerParam = 'answers'
    randomParam = 'random'
    databaseParam = 'database'
    roundCount = 'round'
    if questionParam in kwargs and answerParam in kwargs and kwargs[questionParam] is not None and kwargs[answerParam] is not None:
        question = kwargs[questionParam]
        answers = kwargs[answerParam]
    else:
        # Default - we want a database of multiple questions to draw from. And we wnat to randomly select from that database
        if randomParam in kwargs and kwargs[randomParam] is not True:
            if databaseParam in kwargs and kwargs[databaseParam] is not None and kwargs[databaseParam] is not "":
                import importlib
                mod = importlib.import_module(kwargs[databaseParam])
                db = mod.db
            else:
                from DataBase import db
            question = list(db.keys())[int(kwargs[roundCount]) - 1] # start from index 0
            answers = db[question]
        else:
            import random
            if databaseParam in kwargs and kwargs[databaseParam] is not None and kwargs[databaseParam] is not "":
                import importlib
                mod = importlib.import_module(kwargs[databaseParam])
                db = mod.db
            else:
                from DataBase import db
            question = random.choice(list(db.keys()))
            # Avoid the same question being randomly selected in multiple rounds
            if usedQuestionsParam in kwargs and kwargs[usedQuestionsParam] is not None:
                while question in kwargs[usedQuestionsParam]:
                    question = random.choice(list(db.keys()))
            answers = db[question]
    return (question, answers)

def main(**kwargs):
    playerParam = 'contestants'
    kwargs['round'] = "1"
    g_question, g_answers = GetQuestionAndAnswers(**kwargs)
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
    offsets.Question = 0
    offsets.Names = offsets.Question + 1
    offsets.AnswerBegin = offsets.Names + 1
    offsets.AnswerEnd = offsets.AnswerBegin + len(g_answers) - 1
    offsets.PlayerScore = offsets.AnswerEnd + 1
    offsets.RoundMultiplier = offsets.PlayerScore

    master = tk.Tk()
    PopulateWindow(
        master=master,
        offsets=offsets,
        question=g_question,
        answers=g_answers,
        contestants=g_contestants,
        round=kwargs['round'])
    tk.mainloop()

if __name__ == "__main__":
    # Argparse and sys are for CLI arguments
    # random and DataBase are for default parameters
    import argparse, sys
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
    
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes','true','t','y','1'):
            return True
        elif v.lower() in ('no','false','f','n','0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected')
    
    parser.add_argument('-r','--random',
        type = str2bool,
        nargs = '?',
        const = True,
        default = True,
        help='If set, randomly chooses a prompt from the proided (or default) database file. Else tries to go in order')
    parser.add_argument('-if','--inputfile',
        help='Input Database file. Should match the format of database.py')
        
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
    if ns.random is not None:
        params['random'] = ns.random
    if ns.inputfile is not None:
        params['database'] = ns.inputfile
    main(**params)

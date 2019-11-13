#!python3
# pip install dotmap
import os
import sys
# All classes are defined here as if it were a header
from Classes import *
from dotmap import DotMap
import tkinter as tk

def DisplayTextCallback(Params):
    Params.TextBut.destroy()
    Params.textId = Params.Canvas.create_text(
            Params.start['x'] + (Params.end['x'] - Params.start['x'])/2,
            Params.start['y'] + (Params.end['y'] - Params.start['y'])/2,
            text=Params.text,
            font=("Times",Params.textSize))

def CreateDisplayBox(Params):
    # Window    - Tk window with which to draw upon
    # pos       - {x,y} of location to start from
    # Width     - Width of box
    # height    - Height of box
    # Text      - text to center in box (black)
    # Color     - color to fill box
    Params.Canvas = tk.Canvas(Params.master, width=Params.width, height=Params.height)
    Params.Canvas.pack()
    Params.rectId = Params.Canvas.create_rectangle(
                        Params.start['x'],
                        Params.start['y'],
                        Params.end["x"],
                        Params.end["y"],
                        fill=Params.fill)
    if "hidden" in Params and Params.hidden is True:
        Params.TextBut = tk.Button(Params.master, text="Click to reveal answer")
        # Assign the button action on a new line so we can have a reference to the button itself, and disable after use
        Params.TextBut['command'] = lambda :DisplayTextCallback(Params)
        Params.TextBut.pack()
    else:
        Params.textId = Params.Canvas.create_text(
            Params.start['x'] + (Params.end['x'] - Params.start['x'])/2,
            Params.start['y'] + (Params.end['y'] - Params.start['y'])/2,
            text=Params.text,
            font=("Times",Params.textSize))
    return Params

def main(args):
    # CreateDisplayBox()

    master = tk.Tk()
    
    GameWindow = FullScreenApp(master)
    g_question = "Name a chore that people put off because they have work the next day"
    g_answers = [SurveyAnswer("Take out trash",35), SurveyAnswer("Dishes",30), SurveyAnswer("Vacuum",18), SurveyAnswer("Laundry",6), SurveyAnswer("Clean bathroom",4), SurveyAnswer("Dust",3)]
    g_answertracker = DotMap()
    g_questionObj = DotMap()
    g_questionObj.master = GameWindow.master
    g_questionObj.width = 1000
    g_questionObj.height = 200
    g_questionObj.text = g_question
    g_questionObj.fill = "white"
    g_questionObj.start = {'x':10, 'y':10}
    g_questionObj.end = {'x':990, 'y':190}
    g_questionObj.textSize = 25
    g_questionObj = CreateDisplayBox(g_questionObj)
    for answer in g_answers:
        displaybox_args = DotMap()
        displaybox_args.master = GameWindow.master
        displaybox_args.width = 200
        displaybox_args.height = 50
        displaybox_args.text = answer.response
        displaybox_args.fill = "green"
        displaybox_args.start = {'x':0, 'y':0}
        displaybox_args.end = {'x':100, 'y':50}
        displaybox_args.textSize = 12
        displaybox_args.hidden = True
        g_answertracker[answer.response] = CreateDisplayBox(displaybox_args)

    tk.mainloop()

if __name__ == "__main__":
    main(sys.argv[1:])
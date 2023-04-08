from socket import *
import json
import datetime, threading
import time
import PySimpleGUI as sg
import sys


# Function to fetch localhost's Ipv4 address
if len(sys.argv) > 1:
    HOST = sys.argv[1]
else:
    # If IP address is not provided, get local IP address
    with socket(AF_INET, SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        HOST = s.getsockname()[0]
print(HOST)

def timer():
   now = time.localtime(time.time())
   return now[5]

def showRemainingTime():
    while True:
        time.sleep(10)
        global answered
        global passed_time
        if answered:
            break
        else:
            passed_time += 10
            print(str(passed_time) + " seconds passed!")
        


PORT = 12000
QUIZ = 'QUIZ COMPETITION'

layout = [
          [sg.Text('Please enter your Name')],
          [sg.Text('Name', size=(15, 1)), sg.InputText('name')],
          [sg.Submit()]
         ]

window = sg.Window(QUIZ).Layout(layout)
button, values = window.Read()
if button == 'Submit':
    window.close()
username = values[0]

# Initialize connection
s = socket(AF_INET, SOCK_STREAM) # TCP Socket
s.connect((HOST, PORT))

s.send(username.encode())

# Receive number of questions
questions = int(s.recv(1024).decode())
print("Total # of questions are: " + str(questions))
view_answer = []

for i in range(0, questions):
    # Receive questions
    message = s.recv(1024).decode()
    question = json.loads(message)

    answers = []
    for index, answer in enumerate(question['answers']):
        answers.append(chr(ord('a') + index) + ") " + answer )
    print(answers)

    #print(answers)
    timestamp = datetime.datetime.now()

    # Send contestant answer
    answered = False
    passed_time = 0
    t1 = threading.Thread(target = showRemainingTime)
    t1.start()

    layout = [
        [sg.Text('\nYou have 1 minute to give an answer.\n')],
        [sg.Text(question['question'])],
        [sg.Radio(answers[0], "ANSWER", default=True)],
        [sg.Radio(answers[1], "ANSWER")],
        [sg.Radio(answers[2], "ANSWER")],
        [sg.Radio(answers[3], "ANSWER")],
        [sg.Submit(),sg.Button('Quit')]
    ]
    window = sg.Window(QUIZ).Layout(layout)
    button, values = window.Read()
    window.close()
    print(button)
    print(values)
    for j in values:
        print(values[j])
        if values[j] is True:
            ans = answers[j]
    #for index, j in enumerate(values):
    #    if j is True:
    #       ans = answers[index]
    answered = True
    print(ans[0])
    a = ans[0]
    t1.join()
    if passed_time >= 60:
        print("Timeout! Your answer will not be valid for this question")
        ans = "Timeout"
        s.send(ans[0].encode())
    else:
        s.send(ans[0].encode())


    # Receive answer result
    message = s.recv(1024).decode()
    view_answer.append(message)

print(view_answer)
score_message = s.recv(1024).decode()
print(score_message)
layout = [
          [sg.Text('Your Score is')],
          [sg.Text(score_message)],
          [sg.Text('The winner is:'),sg.Text(winner)]
          [sg.Button('View Answers')]
         ]

s.close()
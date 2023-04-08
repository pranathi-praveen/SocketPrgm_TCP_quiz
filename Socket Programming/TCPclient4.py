from socket import *
import json
import threading

HOST = '192.168.0.191'
PORT = 12000

# Initialize connection (create socket, bind port and listen) 
serverSocket = socket(AF_INET, SOCK_STREAM) # TCP Socket
#HOST = gethostbyname(gethostname())
serverSocket.bind(('', PORT))
serverSocket.listen(45)
print('listening on', (HOST, PORT))

# Open connections
with open('questions.json') as f:
    questions = json.load(f)['questions']

valid_answers = ['a', 'b', 'c', 'd']

# Create a dictionary to store the scores for each player
player_scores = {}
next_player_number = 0

def startContest(s, addr, player_number):
    # Receive username
    username = s.recv(1024).decode()
    print(f"Player {player_number} - {username} connected")
    
    # Get the previous score for this player
    prev_score = player_scores.get(player_number, 0)
    
    # Send the previous score to the client
    s.send(str(prev_score).encode())
    
    points = prev_score

    # Send # of questions
    s.send(str(len(questions)).encode())

    for question in questions:
        # print(question)
        question['msg'] = f"Player {player_number} - Current Points: {points}"
        print(question['msg'])

        # Send questions
        msg = json.dumps(question).encode()
        s.send(msg)

        # Receive answer
        answer = s.recv(1024).decode()
        print(answer)

        # Send answer result
        if answer in valid_answers and answer == valid_answers[question['correct_answer']]:
            points += 10
            #print([question[answer]])
            msg = "The answer is correct!"
            s.send(msg.encode())
        else:
            msg = f"Wrong answer! The correct answer was {valid_answers[question['correct_answer']]}"
            #print([question[answer]])
            s.send(msg.encode())
        s.send((f"Player {player_number} - Total points: {points}").encode())
    
    # Save the final score for this player
    player_scores[player_number] = points
    # Calculate the winner
    max_score = max(player_scores.values())
    winners = [player for player, score in player_scores.items() if score == max_score]

    # Print the winner
    if len(winners) == 1:
        s.send(f"Player {winners[0]} wins with a score of {max_score}!")
    else:
        s.send("It's a tie between players:")
        for winner in winners:
            s.send(f"- Player {winner}")

    
    s.close()


while True:
    s, addr = serverSocket.accept()
    next_player_number += 1
    threading.Thread(target = startContest, args = (s, addr, next_player_number)).start()

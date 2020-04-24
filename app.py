from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from flask_socketio import SocketIO, send, emit, join_room, leave_room, rooms
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import json, random

from player import Player
from game import Game, GamePlayer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
# todo: figure out where the database should live
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///.database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
socketio = SocketIO(app)

games=[]
quizes=[]

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    arcadeScore = db.Column(db.Integer)
    timedScore = db.Column(db.Integer)
    lastPlayed = db.Column(db.DateTime)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    q = db.Column(db.String(150), unique=True)
    answer = db.Column(db.String(150), unique=True)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                global logged_player
                logged_player = Player(user.timedScore,user.arcadeScore,datetime.now())
                return redirect(url_for('mainmenu'))

        return render_template('index.html', form=form, auth="Invalid Username or Password, Please try again")
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('index.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, arcadeScore=0, timedScore=0, lastPlayed=datetime.now())
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            print("An exception occurred")
            return render_template('signup.html', form=form, validation="Username or email already exist. Please try a different one.")
    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/mainmenu')
@login_required
def mainmenu():
    return render_template('mainmenu.html')

@app.route('/deleteaccount')
@login_required
def deletaccount():
    deleteUser(current_user)
    return redirect(url_for('login'))

def deleteUser(user):
    print("deleting: " + str(user))
    db.session.delete(user)
    db.session.commit()


@app.route('/playgame')
@login_required
def playgame():
    lastPlayedTime = current_user.lastPlayed.strftime("%c")
    print(lastPlayedTime)
    print(type(lastPlayedTime))
    logged_player = Player(current_user.timedScore, current_user.arcadeScore, lastPlayedTime)
    return render_template('playgame.html',stats=logged_player, username = current_user.username)

@app.route('/timed')
@login_required
def timed():
    return render_template('timed.html')

@app.route('/arcade')
@login_required
def arcade():
    return render_template('arcade.html')

@app.route('/gameboard')
@login_required
def gameboard():
    duration = request.args.get('duration') or 60
    mode = request.args.get('mode') or 'timed'
    questionBank =  getQuestions()
    # questionBank = [{"1Q": "1"}, {"2Q": "2"}, {"3Q": "3"}, {"4Q": "4"}]
    print(questionBank)
    # x = [{"question": "This is the ninth question?", "answer": "ninth"}]
    questions = json.dumps(questionBank)
    return render_template('gameboard.html', questions = questions, duration = duration, mode = mode, username = current_user.username)
 
@app.route('/multiplayermenu')
@login_required
def multiplayermenu():
    return render_template('multiplayermenu.html')

@app.route('/joinlobby')
@login_required
def joinlobby():
    return render_template('joinlobby.html')

@app.route('/createlobby')
@login_required
def createlobby():
    return render_template('createlobby.html')

@app.route('/multiplayergameboard')
@login_required
def multiplayergameboard():
    return render_template('multiplayergameboard.html')

@app.route('/multiplayerscore')
@login_required
def multiplayerscore():
    return render_template('multiplayerscore.html')

@app.route('/quizmenu')
@login_required
def quizmenu():
    return render_template('quizmenu.html')

@app.route('/quizcreatelobby')
@login_required
def quizcreatelobby():
    return render_template('quizcreatelobby.html')

@app.route('/quizjoinlobby')
@login_required
def quizjoinlobby():
    return render_template('quizjoinlobby.html')

@app.route('/quizscore')
@login_required
def quizscore():
    return render_template('quizscore.html')

@app.route('/leaderboard')
@login_required
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/timedleaderboard')
@login_required
def timedleaderboard():
    data = User.query.order_by(User.timedScore.desc()).all()
    return render_template('timedleaderboard.html', len = len(data), scores = data)

@app.route('/arcadeleaderboard')
@login_required
def arcadeleaderboard():
    data = User.query.order_by(User.arcadeScore.desc()).all()
    return render_template('arcadeleaderboard.html', len = len(data), scores = data)

@app.route('/user', methods=['POST'])
@login_required
def user():
    if request.method == 'POST':
        updateUser(request.get_json())
        return "success"
    return "fail"

@app.route('/validate')
@login_required
def validate():
    pass
    
def updateUser(data):
    uname = data['username']
    mode = data['mode']
    score = data['score']
    current = User.query.filter_by(username=uname).first()
    toUpdate = dict()

    print(mode)
    print(score)

    if mode == 'arcade':
        toUpdate = dict(arcadeScore = (current.arcadeScore + score), lastPlayed = datetime.now())
    else:
        print("else")
        toUpdate = dict(timedScore = (current.timedScore + score), lastPlayed = datetime.now())

    # todo: Check what this is doing?
    # if anything at all... I think it can be removed, probably used for debugging
    admin = User.query.filter_by(username=uname).update(toUpdate)
    db.session.commit()

def getQuestions():
    # Return an dictionary of quetsions qs= [{"question": "answer"}, {"question": "answer"}]
    qs = []
    for _ in range(100):
        qs.append(getDynamicQuestion())
    return qs

def getDynamicQuestion():
    i = random.randint(0,3)
    if i == 0: 
        return getDynamicAddQuestion()
    elif i == 1:
        return getDynamicMultiplyQuestion()
    elif i == 2:
        return getDynamicSubtractQuestion()
    else:
        return getDynamicDivideQuestion()

def getDynamicAddQuestion():
    a = random.randint(1,101)
    b = random.randint(1,101)
    question = "What is {} + {} ?".format(a, b)
    answer = a + b
    return {"question": question, "answer": str(answer)}

def getDynamicSubtractQuestion():
    a = random.randint(1,101)
    b = random.randint(1,101)
    question = "What is {} - {} ?".format(a, b)
    answer = a - b
    return {"question": question, "answer": str(answer)}

def getDynamicMultiplyQuestion():
    a = random.randint(1,101)
    b = random.randint(1,101)
    question = "What is {} * {} ?".format(a, b)
    answer = a * b
    return {"question": question, "answer": str(answer)}

def getDynamicDivideQuestion():
    a = random.randint(51,101)
    b = random.randint(1,20)
    question = "What is {} / {} ?".format(a, b)
    answer = a / b
    return {"question": question, "answer": "{0:.2f}".format(answer)}

def readQuestionsFromDatabase():
    # Read ALL questions from database and return as an array
    questionArr = Question.query.all()
    random.shuffle(questionArr)
    return questionArr
    

def seedQuestions():
    # initialise the database with the questions we can read later
    q1 = Question(q = '1Q', answer = '1')
    q2 = Question(q = '2Q', answer = '2')
    q3 = Question(q = '3Q', answer = '3')
    q4 = Question(q = '4Q', answer = '4')

    db.session().add(q1)
    db.session().add(q2)
    db.session().add(q3)
    db.session().add(q4)

    db.session().commit()

# Temporary
@app.route('/quizhostlobby')
@login_required
def quizhostlobby():
    return render_template('quizhostlobby.html')

@app.route('/hostview')
@login_required
def hostview():
    return render_template('hostview.html')

@app.route('/playerwait')
@login_required
def playerwait():
    return render_template('playerwait.html')

@app.route('/playerview')
@login_required
def playerview():
    return render_template('playerview.html')

def getGameWithPin(pin):
    for game in games:
        if str(pin) == str(game.pin): 
            return game
    return None

def getQuizWithPin(pin):
    for quiz in quizes:
        if str(pin) == str(quiz["pin"]): 
            return quiz
    return None

def getQuestionFromQuiz(quiz, number):
    return {
                "q1": quiz["questions"][number]["question"],
                "a1": quiz["questions"][number]["answers"][0],
                "a2": quiz["questions"][number]["answers"][1],
                "a3": quiz["questions"][number]["answers"][2],
                "a4": quiz["questions"][number]["answers"][3],
                "correct": quiz["questions"][number]["correct"]
            }

def getGameForPlayerId(playerId):
    for game in games:
        if playerId in game.getSids():
            return game
    return None

def getGameForHostId(hostId):
    for game in games:
        if hostId == game.hostId:
            return game
    return None

def getPlayerNames(players):
    arr = []
    for p in players:
        arr.append(p.name)
    return arr

# Socket stuff
@socketio.on('host-join')
def hostJoin(data):
    print(data)
    # When host connects for the first time
    gamePin = data['pin'] or random.randint(1000,9999)
    # Creates a game with pin and host id
    game = Game(gamePin, data['name'])
    if data['mode'] == "multiplayer":
        game.addPlayer(GamePlayer(current_user.username, request.sid, game.hostId))
    games.append(game)
    join_room(gamePin) 
    
    # send('Host has entered the room.', room=gamePin)
    emit('showGamePin', {"pin": str(gamePin)}, room=gamePin)
    emit('updatePlayerLobbyNOW', game.getPlayerNames(), room=game.pin)

    print("sent game pin: " + str(gamePin))

@socketio.on('host-join-game')
def hostJoinGame(data):
    # host_id = str(data['id'])
    pin = str(data['pin'])
    game = getGameWithPin(pin)
    if game is None:
        print("game with pin: {} not found!".format(pin))
    else:
        join_room(pin)
        quiz = getQuizWithPin(pin)
        if quiz is None: 
            print("Quiz not found for pin: {}".format(pin))
        else:
            packetToSend = getQuestionFromQuiz(quiz, 0)
            packetToSend["playersInGame"] = len(game.getPlayerNames())
            packetToSend["pin"] = pin
            packetToSend["questionNum"] = len(quiz["questions"])
            packetToSend["currQuestion"] = game.gameData["currentQuestion"] + 1
            socketio.emit('gameQuestions', packetToSend, room=pin)
            game.gameData["questionLive"] = True
            socketio.emit('gameStartedPlayer', room=pin)

@socketio.on('player-join')
def playerJoin(data):
    playerName = data['name']
    givenPin = data['pin']
    print("player: {} attempting to join with pin: {}".format(playerName, givenPin)) 

    game = getGameWithPin(givenPin)
    if game is None:
        # socketio.emit('noGameFound')
        print("no game found with pin: {}".format(givenPin))
    else:
        print('Found game with given pin: {}'.format(givenPin))
        game.addPlayer(GamePlayer(playerName, request.sid, game.hostId))
        print("Player list for {}:{}".format(givenPin, game.getPlayerNames()))
        join_room(game.pin)
        emit('updatePlayerLobbyNOW', game.getPlayerNames(), room=game.pin)

@socketio.on('player-join-game')
def playerJoinGame(data):
    #  join room
    #  send playerData. ie. all players in that game
    game = getGameForPlayerId(data["id"])
    if game is None:
        print("Unable to get game for player Id: " + data["id"])
    else: 
        join_room(game.pin)
        dataToSend = game.toJSON()
        print(dataToSend)
        emit('playerGameData', dataToSend)


@socketio.on('startGame')
def start(data):
    pin = data['pin']
    mode = data['mode']

    for game in games:
        if pin == str(game.pin):
            join_room(pin)
            if mode == "interactive":
                print("starting {} game: {}".format(mode, pin))
                socketio.emit('gameStarted', {"id":request.sid, "pin":pin, "mode":mode}, room=pin)
            else:
                print("starting {} game: {}".format(mode, pin))
                socketio.emit('gameStartedMultiplayer', {"id":request.sid, "pin":pin, "mode":mode}, room=pin)

        else:
            print("{} game with pin: {} NOT FOUND! Found: {}".format(mode, pin, str(game.pin)))

@socketio.on('playerAnswer')
def playerAnswer(data):
    print("recieved: {}".format(data))
    game = getGameForPlayerId(data["id"])
    player = game.getPlayerWithId(data["id"])
    questionLive = game.gameData["questionLive"]
    quiz = getQuizWithPin(game.pin)
    # socket emit getTime
    answer = int(quiz["questions"][game.gameData["currentQuestion"]]["correct"])

    if questionLive:
        # set player answer 
        player.gamePlayerData["answer"] = data["num"]
        # get correct answer
        # increment game number of players answered
        game.gameData["playersAnswered"] = game.gameData["playersAnswered"] + 1
        playersAnswered = game.gameData["playersAnswered"]

        # update score if correct answer
        if (int(data["num"]) == answer):
            print("Player: {} Answer = {}, Correct = {}, True".format(player.name, data["num"], answer))
            player.gamePlayerData["score"] = player.gamePlayerData["score"] + 100
            request
            socketio.emit("answerResult", True, room=request.sid)
        else: 
            print("Player: {} Answer = {}, Correct = {}, False".format(player.name, data["num"], answer))
            socketio.emit("answerResult", False, room=request.sid)
        
        playersInGame = len(game.getPlayerNames())
        # check if all players have answered
        if (playersInGame == playersAnswered):
            print("{} out of {} players have answered. Question Over.".format(playersAnswered, playersInGame))
            game.gameData["questionLive"] = False
            socketio.emit("questionOver", {"game": game.toJSON(), "correct":answer}, room = game.pin)
        else: 
            print("{} out of {} players have answered. Waiting...".format(playersAnswered, playersInGame))
            # update host screen of num players answered
            socketio.emit("updatePlayersAnswered", {"playersInGame": playersInGame, "playersAnswered": playersAnswered}, room = game.pin)
        

@socketio.on('getScore')
def getScore(data):
    game = getGameForPlayerId(data["id"])
    player = game.getPlayerWithId(data["id"])
    socketio.emit('newScore', player.gamePlayerData["score"], room = request.sid)

@socketio.on('timeUp')
def timeUp(data):
    game = getGameWithPin(data)
    quiz = getQuizWithPin(game.pin)
    answer = int(quiz["questions"][game.gameData["currentQuestion"]]["correct"])
    socketio.emit("questionOver", {"game": game.toJSON(), "correct":answer}, room = game.pin)

def playerSortFunc(p):
    return p.gamePlayerData["score"]

@socketio.on('nextQuestion')
def nextQuestion(data):
    hostId = data 
    # get game
    game = getGameForHostId(hostId)
    if game == None:
        print("Unable to find game for host: {}".format(hostId))
    else: 
        #  reset 'answer' for all players
        for player in game.players:
            player.gamePlayerData["answer"] = 0
        # game player answerd = 0
        game.gameData["playersAnswered"] = 0
        game.gameData["questionLive"] = True
        game.gameData["currentQuestion"] = game.gameData["currentQuestion"] + 1

        #  get quiz
        quiz = getQuizWithPin(game.pin)
        # if more qs
        if (int(game.gameData["currentQuestion"]) < len(quiz["questions"])):
            # create Packet To SEnd
            packetToSend = getQuestionFromQuiz(quiz,game.gameData["currentQuestion"])
            packetToSend["playersInGame"] = len(game.getPlayerNames())
            packetToSend["pin"] = game.pin
            packetToSend["questionNum"] = len(quiz["questions"])
            packetToSend["currQuestion"] = game.gameData["currentQuestion"] + 1
            socketio.emit("gameQuestions", packetToSend)
            socketio.emit('nextQuestionPlayer', room=game.pin)

        # else: emit Game over with name and position as object
        else:
            players = game.players
            players.sort(key = playerSortFunc, reverse=True)
            playerNamesInOrder = getPlayerNames(players)
            playerList = {}
            num = 1
            for p in playerNamesInOrder:
                playerList['num'+str(num)] = p
                num = num + 1
            socketio.emit('GameOver', playerList, room=game.pin)

@socketio.on('getMyQuiz')
def getMyQuiz(data):
    pin = data["pin"]
    quiz = getQuizWithPin(pin)
    if quiz is None:
        print("Quiz not found for pin: {}".format(pin))
    else:
        socketio.emit('initQuiz', quiz["questions"], room = request.sid)

@socketio.on('newQuiz')
def newQuiz(data):
    print("adding quiz {}".format(data))
    quizes.append(data)
    gamepin = data['pin']
    join_room(gamepin) 
    socketio.emit('startGameFromCreator', gamepin, room=gamepin)

@socketio.on('updateMultiplayerScore')
def updateMultiplayerScore(data):
    print(data)

    pin = data["pin"]
    join_room(pin) 
    pid = data["id"]
    score = data["score"]
    game = getGameWithPin(pin)
    player = game.getPlayerWithId(pid)
    player.gamePlayerData["score"] = score
    # socketio.emit('updateLiveScores', gamepin, room=gamepin)

@socketio.on('playerFinishedMultiplayer')
def playerFinishedMultiplayer(data):
    print("data")
    pin = data["pin"]
    pid = data["id"]
    join_room(pin) 

    game = getGameWithPin(pin)
    player = game.getPlayerWithId(pid)
    player.gamePlayerData["finished"] = True

    stats = generateStats(game.players)
    socketio.emit('updateResults', stats, room=pin)
    
def generateStats(players):
    arr = []
    for player in players:
        data = {"name": player.name, "score": player.gamePlayerData["score"], "finished": player.gamePlayerData["finished"]}
        arr.append(data)
    return arr

# debugging endpoints
@socketio.on('getAllGames')
def getAllGames():
    for game in games:
        print("game pin: {}".format(game.pin))
        print("game players: {}".format(game.getPlayerNames()))
        print("game sids: {}".format(game.getSids()))
        print("game: {}".format(game.toJSON()))


@socketio.on('printQuiz')
def printQuiz():
    print(quizes)

@socketio.on('getsocketid')
def sockId():
    print(request.sid)

@socketio.on('test')
def test():
    socketio.emit('GameOver', {}, room=request.sid)



@socketio.on('namespace')
def namespace():
    print(rooms())
    print(request.sid)

if __name__ == '__main__':
    db.create_all()
    socketio.run(app, debug=True)
    

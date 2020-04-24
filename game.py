import json

class Game():
    def __init__(self,pin, hostId):
        self.pin = pin
        self.hostId = hostId
        self.players = []
        self.gameData = {
            "playersAnswered" : 0,
            "questionLive" : True,
            "currentQuestion" : 0
        }

    def addPlayer(self, player):
        self.players.append(player)
    
    def removePlayer(self, player):
        while player in self.players:
            self.players.remove(player)
    
    def getPlayerWithId(self, id):
        for player in self.players:
            if player.sid == id:
                return player
        return None
    
    def getPlayerNames(self):
        arr = []
        for player in self.players:
            arr.append(player.name)
        return arr
    
    def getSids(self):
        arr = []
        for player in self.players:
            arr.append(player.sid)
        return arr

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def __repr__(self):
        return '{}({!r}, {!r}, {!r}, {!r})'.format(
            self.__class__.__name__,
            self.pin, self.hostId, self.getPlayerNames(), self.gameData)

class GamePlayer():
    def __init__(self, name, sid, hostId):
        self.name:str = name
        self.sid: str = sid
        self.hostId = hostId
        self.gamePlayerData = {"score":0, "answer":0, "finished":False}
        
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def __repr__(self):
        return '{}({!r}, {!r}, {!r}, {!r})'.format(
            self.__class__.__name__,
            self.name, self.sid, self.hostId, self.gamePlayerData)

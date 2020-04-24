class Player():
    def __init__(self,timedScore,arcadeScore,lastPlayed):
        self.timedScore = timedScore
        self.arcadeScore = arcadeScore
        self.totalScore = timedScore + arcadeScore
        self.lastPlayed = lastPlayed
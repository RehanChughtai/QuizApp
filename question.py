import json

class Question():
    def __init__(self,question,answer):
        self.question = question
        self.answer = answer

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
import sqlite3
import gui
import operator
import winsound
import thread
import pyttsx
class Player(object):
    def __init__(self,name,id):
        self.name = name
        self.score = 0
        self.id = id
class Question(object):
    def __init__(self,round,category,value,clue,answer,clue_id,cat_id):
        self.round = round
        self.category = category
        self.value = value
        self.clue = clue
        self.answer = answer
        self.daily_double = False
        self.done = False
        self.x,self.y = None,None
        self.clue_id = clue_id
        self.cat_id = cat_id
    def markDone(self):
        self.done = True
    def __lt__ (self, other):
        if self.round != other.round:
            return self.round < other.round
        if self.cat_id != other.cat_id:
            return self.category < other.category
        return self.clue_id < other.clue_id
    def __gt__ (self, other):
        return other.__lt__(self)
    def __eq__ (self, other):
        if other == None:
            return False
        return self.clue_id == other.clue_id
    def __ne__ (self, other):
        return not self.__eq__(other)
    def __str__(self):
        return "Round {}, ${}, Category {} | Q:{}, A:{}".format(self.round,self.value,self.category,self.clue,self.answer)
class GameState(object):
    def __init__(self,board):
        self.show_question = True
        self.board = board
        self.question_interface, root = gui.initializeGUI(self)
        self.board_interface = self.question_interface.status_board
        self.round = 1
        self.players = []
        self.engine = pyttsx.init()
        self.engine.setProperty("rate",140)
        self.last_correct_player = None
        for i,player_name in enumerate(getPlayerNames()):
            self.players.append(Player(player_name,i))
        self.board_interface.setPlayers([p.name for p in self.players])
        for player in self.players:
            self.board_interface.paintScore(player.name,player.score)
        self.paintRound(1)
        self.showQuestion()
        gui.startGUI(root)
    def switchWindows(self):
        self.question_interface.switchWindows()
    def changeQuestion(self,i):
        b = self.board
        curr_question = b.getQuestion(b.question_index)
        curr_question.markDone()
        
        if curr_question.round != 3:
            self.board_interface.remove(curr_question.x,curr_question.y)
        b.question_index += i
        if b.question_index <= 0:
            b.question_index = 0 
        if b.question_index >= len(b.map):
            b.question_index = len(b.map)-1
        if curr_question.round != b.getCurrentQuestion().round:
            self.paintRound(b.getCurrentQuestion().round)
    def paintRound(self,round):
        self.round = round
        if self.round == 3:
            self.board_interface.paintText(3,3,self.board.getCurrentQuestion().category)
            self.question_interface.displayFinalJeopardy({p.name:p.score for p in self.players})
            return
        if self.round < 3:
            self.board_interface.paintCategories(sorted(list(set([q.category for q in self.board.map if q.round == self.round]))))
            starty = (self.round-1)*5
            for x in range(6):
                for y in range(starty,starty+5):
                    q = self.board.getQuestionGrid(x,y)
                    if q == None:
                        continue
                    dy = -5*(q.round-1)
                    self.board_interface.paintRect(x,y,dy=dy)
                    self.board_interface.paintText(x,y,str(q.value),dy=dy)
    def showQuestion(self,toggle=False):
        question = self.board.getCurrentQuestion()
        if question.round == 3:
            return
        if not toggle:
            self.show_question = True
        else:
            self.show_question = not self.show_question
        dy = -5*(question.round-1)
        if question.round != 3:
            self.board_interface.emphasizeQuestion(question.x,question.y,str(question.value),dy=dy)
        self.question_interface.drawQuestion(question,self.show_question)
        if question.daily_double and not toggle:
            player = self.last_correct_player
            if player == None:
                self.board_interface.displayDailyDouble(question,"No one",0)
            else:
                self.board_interface.displayDailyDouble(question,player.name,player.score)
            thread.start_new_thread(playDailyDoubleSound, ())
    def sayQuestion(self):
        self.engine.say(self.board.getCurrentQuestion().clue)
        thread.start_new_thread(self.engine.runAndWait, ())
    def awardQuestion(self,player_id,wrong=False):
        question_value = self.board.getCurrentQuestion().value
        player = self.players[player_id]
        player.score += question_value * (-1 if wrong else 1)
        if not wrong:
            self.last_correct_player = player
        self.board_interface.paintScore(player.name,player.score)
        self.changeQuestion(1)
    def awardPoints(self,player_name,points):
        player = [p for p in self.players if p.name == player_name][0]
        player.score += points
class Board(object):
    def __init__(self,questions):
        self.question_index = 0
        self.map = sorted(questions)
        for round_num in [1,2]:
            values = sorted(list(set([q.value for q in questions if not q.daily_double and q.round==round_num])))
            categories = sorted(list(set([q.category for q in questions if not q.daily_double and q.round==round_num])))
            for i in range(len(self.map)):
                question = self.map[i]
                if question.round!=round_num or question.daily_double:
                    continue
                question.y = (round_num-1)*5+values.index(question.value)
                question.x = categories.index(question.category)
        for i in range(len(self.map)):
            question = self.map[i]
            if question.daily_double:
                if i > 0:
                    prev_question = self.map[i-1]
                    if prev_question.cat_id == question.cat_id:
                        question.x = prev_question.x
                        question.y = prev_question.y+1
                        continue
                if i<len(self.map)-1:
                    next_question = self.map[i+1]
                    if next_question.cat_id == question.cat_id:
                        question.x = next_question.x
                        question.y = next_question.y-1
        for round_num in [1,2]:
            values = sorted(list(set([q.value for q in questions if not q.daily_double and q.round==round_num])))
            for q in [q for q in self.map if q.daily_double and q.round==round_num]:
                q.value = values[q.y -(round_num-1)*5]
    def getQuestion(self,index):
        return self.map[index]
    def getQuestionGrid(self,x,y):
        for q in self.map:
            if q.x == x and q.y == y:
                return q
        return None
    def getCurrentQuestion(self):
        return self.map[self.question_index]
def getPlayerNames():
    return sorted(["Kaighn","Jonah","Shaunak","Will","Tyler"])
def getGameNumber():
    return 4675#4676
def parseQuestions(db_questions):
    questions = [Question(round,category,value,clue,answer,clue_id,cat_id) for round,category,value,clue,answer,clue_id,cat_id in db_questions]
    for q in questions:
        if isinstance(q.value, basestring) and q.round != 3:
            q.daily_double = True
            #q.value = 0
    b = Board(questions)
    return GameState(b)
def playDailyDoubleSound():
    winsound.PlaySound("dailydouble.wav",winsound.SND_FILENAME)    
def main():
    db = sqlite3.connect('C:/Users/Owner/Documents/Github/jeopardy-parser/clues.db')
    cursor = db.cursor()
    game_number = getGameNumber()
    cursor.execute("""SELECT clues.round, categories.category, clues.value, documents.clue, documents.answer,clues.id,categories.id FROM clues,documents,classifications,categories WHERE game = ? AND clues.id = documents.id AND clues.id = classifications.clue_id AND classifications.category_id = categories.id""",(game_number,))
    db_questions = cursor.fetchall()
    state = parseQuestions(db_questions)
if __name__ == '__main__':
    main()
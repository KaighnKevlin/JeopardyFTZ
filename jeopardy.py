import sqlite3
import gui
import operator
import winsound
import thread
class Question(object):
    def __init__(self,round,category,value,clue,answer):
        self.round = round
        self.category = category
        self.value = value
        self.clue = clue
        self.answer = answer
        self.daily_double = False
        self.done = False
    def __str__(self):
        return "Round {}, ${}, Category {} | Q:{}, A:{}".format(self.round,self.value,self.category,self.clue,self.answer)
class GameState(object):
    def __init__(self,board):
        self.show_question = True
        self.board = board
        self.interface, root = gui.initializeGUI(self)
        gui.startGUI(root)
    def changeQuestion(self,i):
        b = self.board
        b.question_index += i
        if b.question_index <= 0:
            b.question_index = 0 
        if b.question_index >= len(b.question_keys):
            b.question_index = len(b.question_keys)-1
    def showQuestion(self,toggle=False):
        question = self.board.getCurrentQuestion()
        if not toggle:
            self.show_question = True
        else:
            self.show_question = not self.show_question
        self.interface.drawQuestion(question,self.show_question)
        if question.daily_double:
            thread.start_new_thread(playDailyDoubleSound, ())
class Board(object):
    def __init__(self,questions):
        self.question_index = 0
        self.map = {(q.round,q.category,q.value):q for q in questions}
        temp_keys = self.map.keys()
        self.question_keys = sorted(temp_keys, key=operator.itemgetter(0,1,2))
    def getQuestion(self,index):
        return self.map[self.question_keys[index]]
    def getCurrentQuestion(self):
        return self.map[self.question_keys[self.question_index]]
    
def getGameNumber():
    return 4676
def parseQuestions(db_questions):
    questions = [Question(round,category,value,clue,answer) for round,category,value,clue,answer in db_questions]
    for q in questions:
        print q
    
    for q in questions:
        if isinstance(q.value, basestring) and q.round != 3:
            q.daily_double = True
            #q.value = 0
    '''
    values = {1:set([]),2:set([])}
    for q in questions:
        if q.round == 1 or q.round == 2:
            values[q.round].add(q.value)
    values1 = list(values[1])
    values1.sort()
    values2 = list(values[2])
    values2.sort()
    num_values = len(values1)
    values1.append(2*values1[-1] - values1[-2])
    '''
    b = Board(questions)
    return GameState(b)
def playDailyDoubleSound():
    winsound.PlaySound("dailydouble.wav",winsound.SND_FILENAME)    
def main():
    db = sqlite3.connect('C:/Users/Owner/Documents/Github/jeopardy-parser/clues.db')
    cursor = db.cursor()
    game_number = getGameNumber()
    cursor.execute("""SELECT clues.round, categories.category, clues.value, documents.clue, documents.answer FROM clues,documents,classifications,categories WHERE game = ? AND clues.id = documents.id AND clues.id = classifications.clue_id AND classifications.category_id = categories.id""",(game_number,))
    db_questions = cursor.fetchall()
    state = parseQuestions(db_questions)
if __name__ == '__main__':
    main()
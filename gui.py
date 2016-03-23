from Tkinter import Tk, Canvas, Frame, BOTH, Text, INSERT, END, CENTER, WORD, Toplevel, W, Y,X,LEFT
import tkFont
import thread

state = None
wrong = False
class QuestionGUI(Frame):
    def __init__(self, parent): 
        Frame.__init__(self, parent)   
        
        self.parent = parent 
        self.parent.bind_all("<Key>", self.key_controller)
        self.initUI()
        self.makeStatusWindow()

    def key_controller(self,event):
        char = event.char
        global wrong
        if char == 'f':
            state.changeQuestion(1)
            state.showQuestion()
        if char == 'b':
            state.changeQuestion(-1)
            state.showQuestion()
        if char == 'a':
            state.showQuestion(toggle=True)
        player_letters = ['j','k','l',';','h']
        if char in player_letters:
            i = player_letters.index(char)
            state.awardQuestion(i,wrong=wrong)
            wrong = False
        if char == 'n':
            wrong = True
            
    def initUI(self):
        self.parent.title("Jeopardy")        
        self.pack(fill=BOTH, expand=1)
        self.text = Text(self,bg="#%02x%02x%02x"%(0,0,58),fg="white")
        self.font = tkFont.Font(family="Courier",weight="bold",size=50)
        self.text.pack(fill=BOTH,expand=1)
        self.text.tag_config("a",justify=CENTER,font=self.font,wrap=WORD)
        self.text.tag_config("b",justify=CENTER,font=self.font,wrap=WORD,foreground="red")

    def drawQuestion(self,question,draw_question):
        self.text.delete(1.0, END)
        tag = "a" if draw_question else "b"
        self.text.insert(INSERT,question.category+"\n",tag)
        self.text.insert(END,"$"+str(question.value)+"\n",tag)
        if draw_question:
            self.text.insert(END,question.clue,"a")
        else:
            self.text.insert(END,question.answer,"a")
    def makeStatusWindow(self):
        self.status_window = Toplevel(self.parent)
        self.status_window.geometry("1300x700+0+0")
        self.status_board = StatusGUI(self.status_window)
class StatusGUI(object):
    def __init__(self,parent):
        self.frame = Frame(parent)  
        self.parent = parent
        self.rect_creator = RectangleCreator(100,50,400,50,1300,700,6,5,2,2)
        self.initUI()
        self.coordsToRectMap = {}
        self.score_ids = {}
    def initUI(self):
        self.frame.pack(fill=BOTH, expand=True)
        self.canvas = Canvas(self.frame,bg="#%02x%02x%02x" % (0, 0, 58))
        self.canvas.pack(fill=BOTH, expand=True)
    def getRect(self,x,y,dy=0):
        if (x,y) in self.coordsToRectMap.keys():
            return self.coordsToRectMap[(x,y)]
        rect = self.rect_creator.create(x,y+dy)
        self.coordsToRectMap[(x,y)] = rect
        return rect
    def remove(self,x,y):
        rect = self.getRect(x,y)
        rect.clear(self.canvas)
    def paintRect(self,x,y,dy=0):
        rect = self.getRect(x,y,dy=dy)
        rect.paintRect(self.canvas)
    def paintText(self,x,y,str,dy=0):
        rect = self.getRect(x,y,dy=dy)
        rect.paintText(self.canvas,str)
    def setPlayers(self,player_names):
        self.player_names = player_names
    def paintScore(self,player_name,score):
        if player_name in self.score_ids:
            self.canvas.delete(self.score_ids[player_name])
        i = self.player_names.index(player_name)
        right_rect = self.getRect(5,0)
        x = right_rect.x2+50
        y = right_rect.y1+i*50+20
        score_id = self.canvas.create_text(x, y, anchor=W,fill="red" ,font="Purisa",text=player_name+": "+str(score))
        self.score_ids[player_name] = score_id
        '''
class GUIQuestion(object):
    def __init__(self,rect,canvas):
        self.rect = rect
        self.canvas = canvas
    def remove(self):
        self.canvas.delete(self.rect_id)
        self.canvas.delete(self.text_id)
    def paint(self,canvas):
        self.rect_id,self.text_id = self.rect.paint(canvas)'''
class RectangleCreator(object):
    def __init__(self,initial_x,initial_y,padmax_x,padmax_y,screen_width,screen_height,num_rects_x,num_rects_y,pad_x,pad_y):
        self.initial_x = initial_x
        self.initial_y = initial_y
        self.x = initial_x
        self.y = initial_y
        self.dx = (screen_width-initial_x-padmax_x)/num_rects_x
        self.dy = (screen_height-initial_y-padmax_y)/num_rects_y
        self.dimensions = (self.dx-2*pad_x,self.dy-2*pad_y)
    def setGrid(self,x,y):
        self.x = self.initial_x + self.dx * x
        self.y = self.initial_y + self.dy * y
    def create(self,x,y):
        self.setGrid(x,y)
        rect = Rectangle(self.x,self.y,self.x+self.dimensions[0],self.y+self.dimensions[1])
        return rect
class Rectangle(object):
    def __init__(self,x1,y1,x2,y2,outline="#%02x%02x%02x" % (0, 0, 69),fill="#%02x%02x%02x" % (0, 0, 175)):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.fill = fill
        self.outline = outline
    def paintRect(self,canvas):
        self.rect_id = canvas.create_rectangle(self.x1,self.y1,self.x2,self.y2, outline=self.outline, fill=self.fill)
    def paintText(self,canvas,str):
        self.text_id = canvas.create_text(self.x1+10, self.y1+20, text=str, anchor=W, font=tkFont.Font(family="Courier",weight="bold",size=25))
    def clear(self,canvas):
        canvas.delete(self.rect_id)
        canvas.delete(self.text_id)
def initializeGUI(game_state):
    global state
    state = game_state
    root = Tk()
    qgui = QuestionGUI(root)
    root.geometry("1300x700+0+0")
    return qgui, root
def startGUI(root):
    root.mainloop()
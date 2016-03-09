from Tkinter import Tk, Canvas, Frame, BOTH, Text, INSERT, END, CENTER, WORD
import tkFont

state = None
class QuestionGUI(Frame):
    def __init__(self, parent): 
        Frame.__init__(self, parent)   
        
        self.parent = parent 
        self.parent.bind_all("<Key>", self.key_controller)
        self.initUI()
        
    def key_controller(self,event):
        char = event.char
        if char == 'f':
            state.changeQuestion(1)
            state.showQuestion()
        if char == 'b':
            state.changeQuestion(-1)
            state.showQuestion()
        if char == 'a':
            state.showQuestion(toggle=True)
        if char == 'j':
            self.incrementFont()
            state.showQuestion()
    def initUI(self):
        self.index = 0
        self.fonts = tkFont.families()
        self.parent.title("Jeopardy")        
        self.pack(fill=BOTH, expand=1)
        self.text = Text(self,bg="#%02x%02x%02x"%(0,0,58),fg="white")
        self.font = tkFont.Font(family="Courier",weight="bold",size=50)
        self.text.pack(fill=BOTH,expand=1)
        self.text.tag_config("a",justify=CENTER,font=self.font,wrap=WORD)
        self.text.tag_config("b",justify=CENTER,font=self.font,wrap=WORD,foreground="red")
        
        '''
        canvas = Canvas(self,bg="#%02x%02x%02x" % (0, 0, 58))
        
        r = Rectangle(100,50,100,50,1300,700,6,5,2,2)
        for i in range(30):
            r.paint(canvas)
        
        canvas.pack(fill=BOTH, expand=1)
        '''
    def incrementFont(self):
        self.font = tkFont.Font(family=self.fonts[self.index],size=50)
        self.index +=1
    def drawQuestion(self,question,draw_question):
        self.text.delete(1.0, END)
        tag = "a" if draw_question else "b"
        self.text.insert(INSERT,question.category+"\n",tag)
        self.text.insert(END,"$"+str(question.value)+"\n",tag)
        if draw_question:
            self.text.insert(END,question.clue,"a")
        else:
            self.text.insert(END,question.answer,"a")
class Rectangle(object):
    def __init__(self,initial_x,initial_y,padmax_x,padmax_y,screen_width,screen_height,num_rects_x,num_rects_y,pad_x,pad_y):
        self.initial_x = initial_x
        self.initial_y = initial_y
        self.x = initial_x
        self.y = initial_y
        self.dx = (screen_width-initial_x-padmax_x)/num_rects_x
        self.dy = (screen_height-initial_y-padmax_y)/num_rects_y
        self.dimensions = (self.dx-2*pad_x,self.dy-2*pad_y)
        self.grid_dimensions = (num_rects_x,num_rects_y)
        self.grid_position = [0,0]
    def move(self):
        self.grid_position[0]+=1
        if self.grid_position[0] == self.grid_dimensions[0]:
            self.grid_position[0] = 0
            self.grid_position[1] += 1
        if self.grid_position[1] >= self.grid_dimensions[1]:
            return
        self.x = self.initial_x + self.dx * self.grid_position[0]
        self.y = self.initial_y + self.dy * self.grid_position[1]
    def paint(self,canvas):
        canvas.create_rectangle(self.x,self.y,self.x+self.dimensions[0],self.y+self.dimensions[1], outline="#%02x%02x%02x" % (0, 0, 69), fill="#%02x%02x%02x" % (0, 0, 175))
        self.move()
def initializeGUI(game_state):
    global state
    state = game_state
    root = Tk()
    ex = QuestionGUI(root)
    root.geometry("1300x700+0+0")
    return ex, root
def startGUI(root):
    root.mainloop()
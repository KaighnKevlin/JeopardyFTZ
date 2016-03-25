from Tkinter import Tk, Canvas, Frame, BOTH, Text, INSERT, END, CENTER, WORD, Toplevel, W, Y,X,LEFT, HIDDEN, Entry, Button, DISABLED
import tkFont
import thread
import utils
import time
state = None
wrong = False

def key_controller(event):
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
        state.showQuestion()
        wrong = False
    if char == 'n':
        wrong = True
    if char == 's':
        state.switchWindows()
    if char == 't':
        state.board_interface.parent.bind_all("<Key>", timer_controller)
    if char == 'S':
        state.sayQuestion()
timer_digits = []
timer_on = False
def timer_controller(event):
    def digits_to_number(lst):
        lst.reverse()
        ret = sum([(10**i)*digit for i,digit in enumerate(timer_digits)])
        lst.reverse()
        return ret
    global timer_digits, timer_on
    char = event.char
    if char >= '0' and char <= '9':
        digit = int(char)
        timer_digits.append(digit)
    if char == 't':
        if timer_on:
            timer_digits = []
            return
        time = digits_to_number(timer_digits)
        timer_digits = []
        state.board_interface.startTimer(time)
        timer_on = True
    if char == 'c':
        state.board_interface.cancel_timer = True
class QuestionGUI(object):
    def __init__(self, parent): 
        self.frame = Frame(parent) 
        self.frame.pack(fill=BOTH,expand=1)
        self.parent = parent 
        self.parent.bind_all("<Key>", key_controller)
        self.initUI()
        self.makeStatusWindow()

    def initUI(self):
        self.parent.title("Jeopardy")        
        self.text = Text(self.frame,bg=utils.bg_blue,fg=utils.mod_question_color)
        self.text.pack(fill=BOTH,expand=1)
        self.text.tag_config("a",justify=CENTER,font=tkFont.Font(family="Courier",weight="bold",size=50),wrap=WORD)
        self.text.tag_config("b",justify=CENTER,font=tkFont.Font(family="Courier",weight="bold",size=50),wrap=WORD,foreground="red")

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
    def switchWindows(self):
        x_q,y_q = self.parent.winfo_x(),self.parent.winfo_y()
        x_s,y_s = self.status_window.winfo_x(),self.status_window.winfo_y()
        self.parent.geometry("1300x700+{}+{}".format(x_s,y_s))
        self.status_window.geometry("1300x700+{}+{}".format(x_q,y_q))

class StatusGUI(object):
    def __init__(self,parent):
        self.frame = Frame(parent)  
        self.parent = parent
        self.rect_creator = RectangleCreator(25,75,400,50,1300,700,6,5,2,2)
        self.initUI()
        self.coordsToRectMap = {}
        self.score_ids = {}
        self.category_ids = []
        self.scores = {}
        self.cancel_timer = False
        #fonts
        self.category_font = tkFont.Font(family="Courier",weight="bold",size=14)
        self.daily_double_font = tkFont.Font(family="Courier",weight="bold",size=50)
        self.daily_double_category_font = tkFont.Font(family="Courier",weight="bold",size=50)
        self.timer_font = tkFont.Font(family="Courier",weight="bold",size=40)
    def initUI(self):
        self.frame.pack(fill=BOTH, expand=True)
        self.canvas = Canvas(self.frame,bg=utils.bg_blue)
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
        right_rect = self.getRect(5,0)
        x = right_rect.x2
        y = right_rect.y1
        self.score_container = ScoreContainer([name for name in player_names],x,y,self.canvas)
    def emphasizeQuestion(self,x,y,str,dy):
        rect = self.getRect(x,y,dy=dy)
        rect.paintText(self.canvas,str,color="red")
    def paintScore(self,player_name,score):
        self.score_container.paintScore(player_name,score)
    
    def paintCategories(self,category_names):
        [self.canvas.delete(id) for id in self.category_ids]
        self.category_ids = []
        for i,name in enumerate(category_names):
            rect = self.getRect(i,0)
            x = rect.x1+10
            y = rect.y1-50
            curr_word = ""
            split = name.split()
            for i,word in enumerate(split):
                if len(curr_word)+len(word) > 12 and curr_word!="":
                    self.category_ids.append(self.canvas.create_text(x,y,fill="white",text=curr_word, anchor=W, font=self.category_font))
                    curr_word=""
                    y+=15
                curr_word+= word+" "
                if i==len(split)-1:
                    self.category_ids.append(self.canvas.create_text(x,y,fill="white",text=curr_word, anchor=W, font=self.category_font))
                    curr_word=""
    def startTimer(self,time):
        self.timer_id = self.canvas.create_text(1100,500,fill="green",text=str(time), anchor=W, font=self.timer_font)
        self.time = time
        def exit():
            self.canvas.delete(self.timer_id)
            self.parent.bind_all("<Key>", key_controller)
            global timer_on
            timer_on = False

        def timerRound():
            if self.cancel_timer:
                self.cancel_timer = False
                exit()
                return
            self.canvas.delete(self.timer_id)
            self.time -= 1
            self.timer_id = self.canvas.create_text(1100,500,fill="green",text=str(self.time), anchor=W, font=self.timer_font)
            if self.time <= 0:
                self.canvas.after(1000,exit)
            else:
                self.canvas.after(1000,timerRound)
        self.canvas.after(1000,timerRound)

    def displayDailyDouble(self,question,player_name,player_score):
        self.canvas.pack_forget()
        dd_screen = [True]
        dd_canvas = Canvas(self.frame,bg=utils.bg_blue)
        dd_canvas.pack(fill=BOTH, expand=True)
        dd_canvas.create_text(50,50,fill="red",text="DAILY DOUBLE: "+player_name+" ($"+str(player_score)+")", anchor=W, font=self.daily_double_font)
        dd_canvas.create_text(50,200,fill="white",text=question.category, anchor=W, font=self.daily_double_category_font)
        def revert():
            dd_canvas.destroy()
            self.canvas.pack(fill=BOTH, expand=True)
        if player_name not in self.player_names:
            self.canvas.after(5000,revert)
            return        
        e = Entry(dd_canvas)
        e.pack()
        
        def temp_controller(event):
            if event.char == 's':
                bool = dd_screen[0]
                forget_canvas = dd_canvas if bool else self.canvas
                paint_canvas = dd_canvas if not bool else self.canvas
                forget_canvas.pack_forget()
                paint_canvas.pack(fill=BOTH, expand=True)
                dd_screen[0] = not bool
        self.parent.bind_all("<Key>", temp_controller)
        def daily_double_key_controller(event):
            char = event.char
            if char == 'n':
                state.awardQuestion(self.player_names.index(player_name),wrong=True)
            if char == 'y':
                state.awardQuestion(self.player_names.index(player_name),wrong=False)
            if char == 'n' or char == 'y':
                self.parent.bind_all("<Key>", key_controller)
                dd_canvas.destroy()
                self.canvas.pack(fill=BOTH, expand=True)
                state.switchWindows()
                state.showQuestion()
            if char == 'a':
                state.showQuestion(toggle=True)


        def placeBet():
            try:
                bet = int(e.get())
            except ValueError:
                e.insert(0,"not a number")
                return
            if bet < 0 or (bet > 2000 and bet > player_score):
                e.insert(0,"invalid bet")
                return
            question.value = bet
            self.parent.bind_all("<Key>", daily_double_key_controller)
            e['state'] = DISABLED
            state.switchWindows()
        b = Button(dd_canvas, text="Place Bet", width=10, command=placeBet)
        b.pack()
class ScoreContainer(object):
    def __init__(self,player_names,initial_x,initial_y,canvas):
        self.canvas = canvas
        self.initial_x,self.initial_y = initial_x,initial_y
        self.player_names = player_names
        self.player_scores = {p:0 for p in self.player_names}
        self.canvas_ids = {}
        self.score_font = tkFont.Font(family="Courier",weight="bold",size=20)
        self.animations = {}
    def getCoordinates(self,player_name):
        x = self.initial_x + 50
        y = self.initial_y+self.player_names.index(player_name)*50+20
        return x,y
    def paintScore(self,player_name,player_score,absolute_position=None):
        self.unpaintScore(player_name)
        if absolute_position == None:
            x,y = self.getCoordinates(player_name)
        else:
            x,y = absolute_position
        canvas_id = self.canvas.create_text(x, y, anchor=W,fill="white",text=player_name+": "+str(player_score),font=self.score_font)
        self.canvas_ids[player_name] = canvas_id
        self.player_scores[player_name] = player_score
        if absolute_position == None:
            self.animate(player_name)
    def unpaintScore(self,player_name):
        if player_name in self.canvas_ids.keys():
            self.canvas.delete(self.canvas_ids[player_name])
            del self.canvas_ids[player_name]
    def animate(self,player_name):
        def switch(p1,p2):
                
            x1,y1 = self.getCoordinates(p1)
            x2,y2 = self.getCoordinates(p2)
            '''
            self.paintScore(p1,self.player_scores[p1],absolute_position=(x2,y2))
            self.paintScore(p2,self.player_scores[p2],absolute_position=(x1,y1))
            
            '''
            for animation in self.animations.keys():
                if animation.player_name == p1 or animation.player_name == p2:
                    self.animations[animation] = False
            p1_animation = LineAnimation(40,x1,y1,x2,y2,p1)
            p2_animation = LineAnimation(40,x2,y2,x1,y1,p2)
            self.animations[p1_animation] = True
            self.animations[p2_animation] = True
            def run_frame():
                if not self.animations[p1_animation] or not self.animations[p2_animation]:
                    p1_animation.done = True
                    del self.animations[p1_animation]
                    p2_animation.done = True
                    del self.animations[p2_animation]
                    return
                x,y = p1_animation.getCoordinates()
                self.paintScore(p1,self.player_scores[p1],absolute_position=(x,y))
                x,y = p2_animation.getCoordinates()
                self.paintScore(p2,self.player_scores[p2],absolute_position=(x,y))
                if p2_animation.done and p1_animation.done:
                    p1_index = self.player_names.index(p1)
                    p2_index = self.player_names.index(p2)
                    self.player_names[p1_index] = p2
                    self.player_names[p2_index] = p1
                    self.animate(player_name)
                    return
                self.canvas.after(17,run_frame)
            run_frame()            
        ranking = self.player_names.index(player_name)
        score = self.player_scores[player_name]
        if ranking > 0:
            higher_player = self.player_names[ranking-1]
            if self.player_scores[higher_player] < score:
                switch(player_name,higher_player)
        if ranking < len(self.player_names)-1:
            lower_player = self.player_names[ranking+1]
            if self.player_scores[lower_player] > score:
                switch(player_name,lower_player)
class LineAnimation(object):
    def __init__(self,timesteps,initial_x,initial_y,dest_x,dest_y,player_name):
        self.player_name = player_name
        self.t = 0
        self.timesteps = timesteps
        self.x = initial_x
        self.y = initial_y
        self.dx = (dest_x-initial_x)/float(timesteps)
        self.dy = (dest_y-initial_y)/float(timesteps)
        self.done = False
    def move(self):
        if self.t >= self.timesteps:
            self.done = True
            return
        else:
            self.t+=1
        self.x += self.dx
        self.y += self.dy
    def getCoordinates(self):
        self.move()
        return self.x,self.y
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
    def __init__(self,x1,y1,x2,y2,outline=utils.rect_outline_blue,fill=utils.rect_blue):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.fill = fill
        self.outline = outline
        self.text_id, self.rect_id = None,None
    def paintRect(self,canvas):
        self.rect_id = canvas.create_rectangle(self.x1,self.y1,self.x2,self.y2, outline=self.outline, fill=self.fill)
    def paintText(self,canvas,str,color=utils.value_color):
        if self.text_id != None:
            canvas.delete(self.text_id)
        self.text_id = canvas.create_text(self.x1+10, self.y1+20, fill=color,text=str, anchor=W, font=tkFont.Font(family="Courier",weight="bold",size=25))
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
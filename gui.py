from Tkinter import Tk, Canvas, Frame, BOTH, Text, INSERT, END, CENTER, WORD, Toplevel, W, Y,X,LEFT, HIDDEN, Entry, Button, DISABLED
import tkFont
import thread
import utils
import time
state = None
wrong = False
def null_controller(event):
    pass
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
    def displayFinalJeopardy(self,player_to_scores_dict):
        player_bets = {}
        player_answers = {}
        self.parent.bind_all("<Key>", null_controller)
        player_names = [t[0] for t in sorted(player_to_scores_dict.items(), key= lambda x : x[1])]
        current_player_index = [0]
        def final_controller(event):
            char = event.char
            if char == 'y':
                right = True
            if char == 'n':
                right = False
            if char == 'y' or char == 'n':
                multiplier = 1 if right else -1
                name = player_names[current_player_index[0]]
                state.awardPoints(name,multiplier*player_bets[name])
                displayFinalJeopardyResult()
        def displayResults(player_name,player_score,player_bet,player_answer):
            self.text.insert(INSERT,"{}'s Answer: {}\nBet: {}".format(player_name,player_answer,player_bet),"b")
        def displayFinalJeopardyResult():
            self.text.delete(1.0, END)
            for child in self.text.winfo_children():
                child.destroy()
            current_player_index[0] += 1
            if current_player_index[0] >= len(player_names):
                return
            current_player = player_names[current_player_index[0]]
            displayResults(current_player,player_to_scores_dict[current_player],player_bets[current_player],player_answers[current_player])
            self.parent.bind_all("<Key>", final_controller)

        def displayFinalJeopardyBet(player_name,player_score,answer=False):
            self.text.delete(1.0, END)
            for child in self.text.winfo_children():
                child.destroy()
            mode = "Bet" if not answer else "Answer"
            self.text.insert(INSERT,"Final Jeopardy\n{}'s {} (${}):".format(player_name,mode,str(player_score)),"b")
            e = Entry(self.text)
            e.pack()
            def placeBet():
                if not answer:
                    try:
                        bet = int(e.get())
                    except ValueError:
                        e.insert(0,"not a number")
                        return
                    if bet < 0 or bet > player_score:
                        e.insert(0,"invalid bet")
                        return
                    player_bets[player_name] = bet
                else:
                    input = e.get()
                    player_answers[player_name] = input
                
                current_player_index[0] += 1
                if current_player_index[0] >= len(player_names):
                    if not answer:
                        current_player_index[0] = 0
                        next_player = player_names[0]
                        displayFinalJeopardyBet(next_player,player_to_scores_dict[next_player],answer=True)
                    else:
                        current_player_index[0] = 0
                        displayFinalJeopardyResult()
                else:
                    next_player = player_names[current_player_index[0]]
                    displayFinalJeopardyBet(next_player,player_to_scores_dict[next_player],answer=answer)
            b = Button(self.text, text="Place Bet", width=10, command=placeBet)
            b.pack()
            
            
        displayFinalJeopardyBet(player_names[current_player_index[0]],player_to_scores_dict[player_names[current_player_index[0]]])

class StatusGUI(object):
    def __init__(self,parent):
        self.frame = Frame(parent)  
        self.parent = parent
        self.rect_creator = RectangleCreator(25,75,400,50,1300,700,6,5,2,2)
        self.initUI()
        self.coordsToRectMap = {}
        self.cancel_timer = False
    def initUI(self):
        self.frame.pack(fill=BOTH, expand=True)
        self.canvas = utils.JCanvas(self.frame,bg=utils.bg_blue)
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
        self.canvas.delete("category")
        for i,name in enumerate(category_names):
            rect = self.getRect(i,0)
            x = rect.x1+3
            y = rect.y1-100
            f = Frame(self.canvas,width=120,height=55)
            t = Text(f,bg=utils.bg_blue,fg=utils.mod_question_color,borderwidth=0)
            t.tag_config("c",justify=CENTER,font=self.canvas.fonts.getFont("category_font"),wrap=WORD)
            t.insert(INSERT,name,"c")
            t.config(state=DISABLED)
            t.pack(fill=BOTH,expand=True)
            f.pack_propagate(False)
            f.place(x=x,y=y)
    def startTimer(self,time):
        self.timer_id = self.canvas.writeText(1100,500,"timer_font",fill="green",text=str(time), anchor=W)
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
            self.timer_id = self.canvas.writeText(1100,500,"timer_font",fill="green",text=str(self.time), anchor=W)
            if self.time <= 0:
                self.canvas.after(1000,exit)
            else:
                self.canvas.after(1000,timerRound)
        self.canvas.after(1000,timerRound)
    def displayDailyDouble(self,question,player_name,player_score):
        self.canvas.pack_forget()
        dd_screen = [True]
        dd_canvas = utils.JCanvas(self.frame,bg=utils.bg_blue)
        dd_canvas.pack(fill=BOTH, expand=True)
        dd_canvas.writeText(50,50,"daily_double_font",fill="red",text="DAILY DOUBLE: "+player_name+" ($"+str(player_score)+")", anchor=W)
        dd_canvas.writeText(50,200,"daily_double_category_font",fill="white",text=question.category, anchor=W)
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
    def getCoordinates(self,player_name):
        x = self.initial_x + 50
        y = self.initial_y+self.player_names.index(player_name)*50+20
        return x,y
    def paintScore(self,player_name,player_score):
        ids_tuple = self.canvas.find_withtag(player_name)
        if len(ids_tuple) == 0:
            x,y = self.getCoordinates(player_name)
            canvas_id = self.canvas.writeText(x, y, "score_font", anchor=W, fill="white",text="",tags=player_name)
        else:
            canvas_id = ids_tuple[0]
        self.canvas.itemconfig(canvas_id,text=player_name+": "+str(player_score))
        self.player_scores[player_name] = player_score
        self.animate()
    def animate(self):
        def switch(p1,p2):
            self.canvas.animateLine3(p1,p2,40,17)
            p1_index = self.player_names.index(p1)
            p2_index = self.player_names.index(p2)
            self.player_names[p1_index] = p2
            self.player_names[p2_index] = p1
        for i,player in enumerate(self.player_names):
            if i==0:
                continue
            score = self.player_scores[player]
            other_score = self.player_scores[self.player_names[i-1]]
            if score > other_score:
                switch(player,self.player_names[i-1])
                self.animate()
                return
        
class RectangleCreator(object):
    def __init__(self,initial_x,initial_y,padmax_x,padmax_y,screen_width,screen_height,num_rects_x,num_rects_y,pad_x,pad_y):
        self.initial_x = initial_x
        self.initial_y = initial_y
        self.dx = (screen_width-initial_x-padmax_x)/num_rects_x
        self.dy = (screen_height-initial_y-padmax_y)/num_rects_y
        self.dimensions = (self.dx-2*pad_x,self.dy-2*pad_y)
    def create(self,x,y):
        place_x,place_y = self.initial_x+self.dx*x, self.initial_y+self.dy*y
        rect = Rectangle(place_x,place_y,place_x+self.dimensions[0],place_y+self.dimensions[1])
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
        self.rect_id = canvas.t2(canvas.create_rectangle,self.x1,self.y1,self.x2,self.y2,outline=self.outline, fill=self.fill)
    def paintText(self,canvas,str,color=utils.value_color):
        if self.text_id != None:
            canvas.delete(self.text_id)
        self.text_id = canvas.writeText(self.x1+10, self.y1+20, "text_font", fill=color,text=str, anchor=W)
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
import tkFont
from Tkinter import *
bg_blue = "#%02x%02x%02x"%(0,0,58)
rect_outline_blue = "#%02x%02x%02x" % (0, 0, 69)
rect_blue = "#%02x%02x%02x" % (0, 0, 175)
mod_question_color = "white"
value_color = "#%02x%02x%02x"%(255,255,0)

class SuperCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height,self.original_height = 700,700
        self.width,self.original_width = 1300,1300
        
    def on_resize(self,event):
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)
    def t2(self,f,x1,y1,x2,y2,**kwargs):
        return f(*(self.transform(x1,y1)+self.transform(x2,y2)),**kwargs)
    def t1(self,f,x,y,**kwargs):
        return f(*(self.transform(x,y)),**kwargs)
    def transform(self,x,y):
        wscale = float(self.width)/self.original_width
        hscale = float(self.height)/self.original_height
        return (x*wscale,y*hscale)
        
import tkFont
from Tkinter import Canvas, W
bg_blue = "#%02x%02x%02x"%(0,0,58)
rect_outline_blue = "#%02x%02x%02x" % (0, 0, 69)
rect_blue = "#%02x%02x%02x" % (0, 0, 175)
mod_question_color = "white"
value_color = "#%02x%02x%02x"%(255,255,0)

class SuperCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self._on_resize)
        self.height,self.original_height = 700,700
        self.width,self.original_width = 1300,1300
        self.fonts = FontContainer()
    def _on_resize(self,event):
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        self.config(width=self.width, height=self.height)
        self.scale("all",0,0,wscale,hscale)
        wscale_original = float(self.width)/self.original_width
        hscale_original = float(self.height)/self.original_height
        self.fonts.scale((wscale_original+hscale_original)/2.0)
    def t2(self,f,x1,y1,x2,y2,**kwargs):
        return f(*(self._transform(x1,y1)+self._transform(x2,y2)),**kwargs)
    def t1(self,f,x,y,**kwargs):
        return f(*(self._transform(x,y)),**kwargs)
    def writeText(self,x,y,font_str,**kwargs):
        tags = kwargs.get("tags",())
        kwargs["tags"] = tuple(["canvas_text"]+[t for t in tags])
        return self.create_text(*self._transform(x,y),font=self.fonts.getFont(font_str),**kwargs)
    def _transform(self,x,y):
        wscale = float(self.width)/self.original_width
        hscale = float(self.height)/self.original_height
        return x*wscale,y*hscale
class JCanvas(SuperCanvas):
    def __init__(self,parent,**kwargs):
        SuperCanvas.__init__(self,parent,**kwargs)
        self.fonts.add("category_font",tkFont.Font(family="Courier",weight="bold",size=14))
        self.fonts.add("daily_double_font",tkFont.Font(family="Courier",weight="bold",size=50))
        self.fonts.add("daily_double_category_font",tkFont.Font(family="Courier",weight="bold",size=50))
        self.fonts.add("timer_font",tkFont.Font(family="Courier",weight="bold",size=40))
        self.fonts.add("score_font",tkFont.Font(family="Courier",weight="bold",size=20))
        self.fonts.add("text_font",tkFont.Font(family="Courier",weight="bold",size=25))
        
        
class FontContainer(object):
    def __init__(self):
        self.fonts = {}
        self.font_original_sizes = {}
    def getFont(self,font_str):
        return self.fonts[font_str]
    def scale(self,scalar):
        for font_str,font in self.fonts.items():
            original_size = self.font_original_sizes[font_str]
            font.configure(size=int(round(original_size-original_size*(1-scalar))))
    def add(self,font_str,font):
        self.fonts[font_str] = font
        self.font_original_sizes[font_str] = font["size"]
        
    
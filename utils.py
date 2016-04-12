import tkFont
from Tkinter import Canvas, W
import time
import thread
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
        self.animations = {}
        self.animation_queue = []
        self.children_original_dimensions = {}
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
        o_wscale,o_hscale = self._getScalars()
        for child in self.winfo_children():
            has_width = True
            if child not in self.children_original_dimensions.keys():
                try:
                    self.children_original_dimensions[child] = (child["width"],child["height"],child.winfo_x(),child.winfo_y())
                except:
                    self.children_original_dimensions[child] = (0,0,child.winfo_x(),child.winfo_y())
            dim = self.children_original_dimensions[child]
            child.place(x=int(dim[2]*o_wscale),y=int(dim[3]*o_hscale))
            try:
                child.configure(width=int(dim[0]*o_wscale),height=int(dim[1]*o_hscale))
            except:
                pass
    def t2(self,f,x1,y1,x2,y2,**kwargs):
        return f(*(self._transform(x1,y1)+self._transform(x2,y2)),**kwargs)
    def t1(self,f,x,y,**kwargs):
        return f(*(self._transform(x,y)),**kwargs)
    def writeText(self,x,y,font_str,**kwargs):
        tags = kwargs.get("tags",())
        if isinstance(tags,tuple):
            kwargs["tags"] = tuple(["canvas_text"]+[t for t in tags])
        else:
            kwargs["tags"] = ("canvas_text",tags)
        return self.create_text(*self._transform(x,y),font=self.fonts.getFont(font_str),**kwargs)
    def _transform(self,x,y):
        wscale,hscale = self._getScalars()
        return x*wscale,y*hscale
    def _untransform(self,x,y):
        wscale,hscale = self._getScalars()
        return x/wscale,y/hscale
    def _getScalars(self):
        return float(self.width)/self.original_width,float(self.height)/self.original_height
    
    def animateLineId(self,animate_id,dest_x,dest_y,steps_num,t_delta): 
        animation = LineAnimation(animate_id,steps_num,dest_x,dest_y,t_delta,self)
        if animate_id not in self.animations.keys():
            self.animations[animate_id] = animation
        else:
            self.animations[animate_id].done = True
            self.animations[animate_id] = animation
        animation.animate()
    def animateLine(self,animate_tag,dest_x,dest_y,steps_num,t_delta): 
        ids_tuple = self.find_withtag(animate_tag)
        for id in ids_tuple:
            self.animateLineId(id,dest_x,dest_y,steps_num,t_delta)
    def animateLine3(self,tag1,tag2,steps_num,t_delta):
        id1 = self.find_withtag(tag1)[0]
        id2 = self.find_withtag(tag2)[0]
        if id1 in self.animations.keys() and not self.animations[id1].done or id2 in self.animations.keys() and not self.animations[id2].done:
            self.animation_queue.append((id1,id2))
        else:
            dest_x,dest_y = self.coords(id2)
            self.animateLine(tag1,dest_x,dest_y,steps_num,t_delta)
            dest_x,dest_y = self.coords(id1)
            self.animateLine(tag2,dest_x,dest_y,steps_num,t_delta)
    def runAnimations(self):
        if len(self.animation_queue) > 0:
            id1,id2 = self.animation_queue[0]
            if not (id1 in self.animations.keys() and not self.animations[id1].done or id2 in self.animations.keys() and not self.animations[id2].done):
                del self.animation_queue[0]
                dest_x,dest_y = self.coords(id2)
                self.animateLineId(id1,dest_x,dest_y,40,17)
                dest_x,dest_y = self.coords(id1)
                self.animateLineId(id2,dest_x,dest_y,40,17)
                
                    
class LineAnimation(object):
    def __init__(self,id,timesteps,dest_x,dest_y,t_delta,canvas):
        self.done = False
        self.id = id
        self.t = 0
        self.timesteps = timesteps
        self.initial_x,self.initial_y = canvas._untransform(*canvas.coords(id))
        self.dest_x, self.dest_y = canvas._untransform(dest_x,dest_y)
        self.dx = (self.dest_x-self.initial_x)/float(timesteps)
        self.dy = (self.dest_y-self.initial_y)/float(timesteps)
        self.t_delta = t_delta
        self.canvas = canvas
    def animate(self): 
        def run_frame():
            self.t += 1
            if self.done or self.t > self.timesteps:
                self.done = True
                self.canvas.runAnimations()
                return
            dest_point = (self.dx*self.t+self.initial_x,self.dy*self.t+self.initial_y)
            cur_point = self.canvas._untransform(*self.canvas.coords(self.id))
            vector = (dest_point[0]-cur_point[0],dest_point[1]-cur_point[1])
            resized_vector = self.canvas._transform(*vector)
            self.canvas.move(self.id,*resized_vector)
            self.canvas.after(self.t_delta,run_frame)
        self.canvas.after(0,run_frame)
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
        
    
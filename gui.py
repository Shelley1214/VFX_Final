import tkinter as tk
from tkinter import filedialog as fido
from PIL import ImageTk, Image
from cloning import Cloning
import numpy as np

class GUI(Cloning):

    def __init__(self, master, title = "Image Loader"):

        super().__init__()
        self.master = master

        self.error_message = tk.Label(self.master, text="", fg='red')
        self.error_message.grid(row = 2, column = 0)
        self.canvas = tk.Canvas(self.master)
        self.canvas.grid(row = 3, column = 0)
        self.canvas_shape = 600

        self.image_button = tk.Button(self.master, font = "Helvetica 12",text = "Choose Source Image", command = self.choose_source_image)
        self.image_button.grid(row = 4, column = 0, sticky = tk.NSEW)

        self.settingButtons = tk.Frame(self.master)
        self.settingButtons.grid(row = 1, column = 0)

        self.QuickStart = tk.Button(self.master, font = "Helvetica 12",text = "QuickStart", command = self.QuickStart)
        self.QuickStart.grid(row = 1, column = 1)

        self.image_button = tk.Button(self.master, font = "Helvetica 12",text = "Choose Target Image", command = self.choose_target_image)
        self.image_button.grid(row = 4, column = 1, sticky = tk.NSEW)
        self.canvas1 = tk.Canvas(self.master)
        self.canvas1.grid(row = 3, column = 1)

        self.button1 = tk.Button(self.settingButtons, font = "Helvetica 12",text = "Undo", command = self.undo)
        self.button2 = tk.Button(self.settingButtons, font = "Helvetica 12",text = "Clear", command = self.clear)
        self.button3 = tk.Button(self.settingButtons, font = "Helvetica 12", text = "Done", command = self.done)
        self.button4 = tk.Button(self.settingButtons, font = "Helvetica 12", text = "+", command = self.zoom_in)
        self.button5 = tk.Button(self.settingButtons, font = "Helvetica 12", text = "-", command = self.zoom_out)

        self.button4.pack(side=tk.LEFT)
        self.button5.pack(side=tk.LEFT)
        self.button1.pack(side=tk.LEFT)
        self.button2.pack(side=tk.LEFT)
        self.button3.pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.source_click)
        self.canvas1.bind("<Button-1>", self.target_click)

        self.line = []
        self.load_source_image = False
        self.load_target_image = False
        self.load_trimap_image = False
        self.mode = 'mesh'
        self.scale = 1

        self.var1 = tk.IntVar()
        self.var1.set(3)
        self.mode_btn = tk.Frame(self.master)
        self.mode_btn.grid(row = 0, column = 0)
        self.checkbutton1 = tk.Checkbutton(self.mode_btn, text='cv2',variable=self.var1, onvalue=1, command = lambda: self.checkbutton_event(self.checkbutton1))
        self.checkbutton2 = tk.Checkbutton(self.mode_btn, text='mvc', variable=self.var1, onvalue=2, command = lambda: self.checkbutton_event(self.checkbutton2))
        self.checkbutton3 = tk.Checkbutton(self.mode_btn, text='mesh', state='disabled', variable=self.var1, onvalue=3, command = lambda: self.checkbutton_event(self.checkbutton3))
        self.checkbutton1.pack(side=tk.LEFT)
        self.checkbutton2.pack(side=tk.LEFT)
        self.checkbutton3.pack(side=tk.LEFT)

    def checkbutton_event(self,widget):
        
        self.mode =  widget['text']

        self.checkbutton1['state'] = 'normal'
        self.checkbutton2['state'] = 'normal'
        self.checkbutton3['state'] = 'normal'

        if widget['text'] == 'cv2':
            self.checkbutton1['state'] = 'disabled'
        elif widget['text'] == 'mvc':
            self.checkbutton2['state'] = 'disabled'
        else:
            self.checkbutton3['state'] = 'disabled'


    def QuickStart(self):

        target = "image/target.jpeg"
        source = "image/source.jpeg"

        self.source_image = Image.open(source)
        self.source = ImageTk.PhotoImage(self.source_image)
        sw, sh = self.source.width(),self.source.height()
        self.load_source_image = True

        self.target_image = Image.open(target)
        self.target = ImageTk.PhotoImage(self.target_image)
        tw, th = self.target.width(),self.target.height()
        self.load_target_image = True

        self.canvas.config(width = self.canvas_shape, height = sh)
        self.canvas.create_image((self.canvas_shape//2, sh//2), image = self.source, anchor = tk.CENTER)
        self.canvas1.config(width = tw, height = th)
        self.canvas1.create_image((0,0), image = self.target, anchor = tk.NW)
        self.pts = np.load('border.npy')

        for i in range(len(self.pts)-1):
            offset = self.canvas_shape // 2 - sw // 2
            points = [self.pts[i][0] + offset, self.pts[i][1], self.pts[i+1][0] + offset, self.pts[i+1][1]]
            self.line.append(self.canvas.create_line(points[0], points[1], points[2], points[3], fill="red", width=1))


    def image_cloniing(self, center):
        if self.mode == "cv2":
            result = self.OpenCV_Cloning(center)
        elif self.mode == "mvc":
            result = self.seamlessClone(center)
        else:
            result = self.seamlessClone_mesh(center)
        return result

    def scale_source_image(self):
        w, h = self.source.width(),self.source.height()
        self.source_image = self.source_image.resize((int(w * self.scale), int(h * self.scale)))
        self.source = ImageTk.PhotoImage(self.source_image,  master = self.master)
        w, h = self.source.width(),self.source.height()

        self.canvas.config(width = self.canvas_shape, height = h)
        self.canvas.create_image((self.canvas_shape//2, h//2), image = self.source, anchor = tk.CENTER)
        if len(self.pts) != 0:
            self.pts = (self.pts * self.scale).astype(int)
            for l in self.line:
                self.canvas.delete(l)
            self.line = []
            for i in range(len(self.pts)-1):
                offset = self.canvas_shape // 2 - w // 2
                points = [self.pts[i][0] + offset, self.pts[i][1], self.pts[i+1][0] + offset, self.pts[i+1][1]]
                self.line.append(self.canvas.create_line(points[0], points[1], points[2], points[3], fill="red", width=1))

    def zoom_in(self):
        if self.load_source_image:
            self.scale = 1.05
            if self.source.width() * self.scale <= self.canvas_shape:
                self.scale_source_image()

    def zoom_out(self):
        if self.load_source_image:
            self.scale = 0.95
            if self.source.width() * self.scale >= 200:
                self.scale_source_image()

    def target_click(self, event):
        if not self.load_target_image:
            return
        if len(self.line) == 0: 
            return
        print ("[target] clicked at", event.x, event.y)
        self.result = self.image_cloniing(np.array([event.x, event.y]))
        self.show_clonning()
        
    def target_click_mat(self, event):
        if not self.load_target_image:
            return
        if len(self.line) == 0: 
            return
        print ("[target] clicked at", event.x, event.y)
        self.result = self.matting(( event.x, event.y))
        self.show_clonning()


    def source_click(self,event):
        if not self.load_source_image :
            return
        print ("[source] clicked at", event.x, event.y)
        w = self.source.width()
        offset = self.canvas_shape // 2 - w // 2
        if len(self.pts) == 0:
            x1, y1 = ( event.x - 1 ), ( event.y - 1 )
            x2, y2 = ( event.x + 1 ), ( event.y + 1 )
            self.line.append(self.canvas.create_oval( x1, y1, x2, y2, fill = "red", width=1 ))
            self.pts = np.vstack((self.pts, [event.x - offset, event.y]))
            return

        x1 = self.pts[-1][0] + offset
        y1 = self.pts[-1][1]
        x2 = event.x
        y2 = event.y
        self.pts = np.vstack((self.pts, [event.x - offset, event.y]))
        self.line.append(self.canvas.create_line(x1,y1,x2,y2,fill="red", width=1))

    def choose_target_image(self):
        image_name = fido.askopenfilename(title = "Target image")
        if image_name:
            self.target_image = Image.open(image_name)
            self.target = ImageTk.PhotoImage(self.target_image )
            w, h = self.target.width(),self.target.height()
            self.canvas1.config(width = w, height = h)
            self.canvas1.create_image((0,0), image = self.target, anchor = tk.NW)
            self.load_target_image = True

    def show_clonning(self):
        if self.result is None:
            self.error_message['text'] = 'ERROR operation!!'
        else:  
            self.result = Image.fromarray(self.result)
            self.result = ImageTk.PhotoImage(self.result,  master = self.master)
            self.canvas1.create_image((0,0), image = self.result, anchor = tk.NW)
            self.error_message['text'] = ''

    def choose_source_image(self):
        image_name = fido.askopenfilename(title = "Source image")
        if image_name:
            self.source_image = Image.open(image_name)
            self.source = ImageTk.PhotoImage(self.source_image)
            w, h = self.source.width(),self.source.height()
            self.canvas.config(width = self.canvas_shape, height = h)
            self.canvas.create_image((self.canvas_shape//2, h//2), image = self.source, anchor = tk.CENTER)
            self.load_source_image = True

    def clear(self):
        if len(self.line) != 0: 
            for l in self.line:
                self.canvas.delete(l)
            self.line = []
            self.pts = np.empty((0, 2), dtype=int)
        
    def undo(self):
        if len(self.line) != 0: 
            self.canvas.delete(self.line.pop())
            if len(self.pts) != 0:
                self.pts = self.pts[:-1]
        
    def done(self):
        if len(self.line) == 0: 
            return
        
        w = self.source.width()
        offset = self.canvas_shape // 2 - w // 2
        self.line.append(self.canvas.create_line(self.pts[-1][0] + offset, self.pts[-1][1], self.pts[0][0] + offset, self.pts[0][1],fill="red", width=1))
        self.pts = np.vstack((self.pts, self.pts[0]))
        w, h = self.target.width(),self.target.height()

        # Clonning
        self.result = self.image_cloniing(np.array([w//2, h//2]))
        self.show_clonning()



    def mat(self):
        w, h = self.target.width(),self.target.height()
        self.result = self.matting( (w//2, h//2))
        self.show_clonning()
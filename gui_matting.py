import tkinter as tk
from tkinter import filedialog as fido
from PIL import ImageTk, Image
from cloning import Cloning

class GUI_matting(Cloning):

    def __init__(self, master, title = "Image Loader"):

        super().__init__()

        self.master = master
        self.canvas = tk.Frame(self.master)
        self.canvas.grid(row = 2, column = 0)
        self.canvas_shape = 600
        self.canvas_1 = tk.Canvas(self.canvas)
        self.canvas_1.pack(fill='x')
        self.canvas_2 = tk.Canvas(self.canvas)
        self.canvas_2.pack(fill='x')

        self.source_image_button = tk.Frame(self.master)
        self.source_image_button.grid(row = 3, column = 0, sticky = tk.NSEW)

        self.image_button1 = tk.Button(self.source_image_button, font = "Helvetica 12",text = "Choose Source Image", command = self.choose_source_image)
        self.image_button1.pack(fill='x')
        self.image_button2 = tk.Button(self.source_image_button, font = "Helvetica 12",text = "Choose Trimap Image", command = self.choose_trimap_image)
        self.image_button2.pack(fill='x')

        self.settingButtons = tk.Frame(self.master)
        self.settingButtons.grid(row = 1, column = 0)

        self.QuickStart = tk.Button(self.master, font = "Helvetica 12",text = "QuickStart", command = self.QuickStart)
        self.QuickStart.grid(row = 1, column = 1)

        self.image_button = tk.Button(self.master, font = "Helvetica 12",text = "Choose Target Image", command = self.choose_target_image)
        self.image_button.grid(row = 3, column = 1, sticky = tk.NSEW)
        self.canvas1 = tk.Canvas(self.master)
        self.canvas1.grid(row = 2, column = 1)

        self.button = tk.Button(self.settingButtons, font = "Helvetica 12", text = "Matting", command = self.done)
        self.button1 = tk.Button(self.settingButtons, font = "Helvetica 12", text = "+", command = self.zoom_in)
        self.button2 = tk.Button(self.settingButtons, font = "Helvetica 12", text = "-", command = self.zoom_out)

        self.button1.pack(side=tk.LEFT)
        self.button2.pack(side=tk.LEFT)
        self.button.pack(side=tk.LEFT)
        self.canvas1.bind("<Button-1>", self.target_click)

        self.load_source_image = False
        self.load_target_image = False
        self.load_trimap_image = False
        self.mode = 'mesh'
        self.var1 = tk.IntVar()
        self.var1.set(3)
        self.mode_btn = tk.Frame(self.master)
        self.mode_btn.grid(row = 0, column = 0)
        self.checkbutton2 = tk.Checkbutton(self.mode_btn, text='mvc', variable=self.var1, onvalue=2, command = lambda: self.checkbutton_event(self.checkbutton2))
        self.checkbutton3 = tk.Checkbutton(self.mode_btn, text='mesh', state='disabled', variable=self.var1, onvalue=3, command = lambda: self.checkbutton_event(self.checkbutton3))
        self.checkbutton2.pack(side=tk.LEFT)
        self.checkbutton3.pack(side=tk.LEFT)

    def checkbutton_event(self,widget):
        
        self.mode =  widget['text']

        self.checkbutton2['state'] = 'normal'
        self.checkbutton3['state'] = 'normal'

        if widget['text'] == 'mvc':
            self.checkbutton2['state'] = 'disabled'
        else:
            self.checkbutton3['state'] = 'disabled'


    def QuickStart(self):
        target = "image/background.jpeg"
        source = "image/input.png"
        trimap = "image/trimap.png"
        self.source_image = Image.open(source)
        self.source = ImageTk.PhotoImage(self.source_image,  master = self.master)
        w, h = self.source.width(),self.source.height()
        self.canvas_1.config(width = self.canvas_shape, height = h)
        self.canvas_1.create_image((self.canvas_shape//2, h//2), image = self.source, anchor = tk.CENTER)
        self.load_source_image = True

        self.trimap_image = Image.open(trimap)
        self.trimap = ImageTk.PhotoImage(self.trimap_image,  master = self.master)
        w, h = self.trimap.width(),self.trimap.height()
        self.canvas_2.config(width = self.canvas_shape, height = h)
        self.canvas_2.create_image((self.canvas_shape//2, h//2), image = self.trimap, anchor = tk.CENTER)
        self.load_trimap_image = True

        self.target_image = Image.open(target)
        self.target = ImageTk.PhotoImage(self.target_image,  master = self.master)
        w, h = self.target.width(),self.target.height()
        self.canvas1.config(width = w, height = h)
        self.canvas1.create_image((0,0), image = self.target, anchor = tk.NW)
        self.load_target_image = True



    def target_click(self, event):
        if self.load_target_image and self.load_source_image and self.load_trimap_image:
            print ("[target] clicked at", event.x, event.y)
            self.result = self.matting(( event.x, event.y), self.mode)
            self.show_clonning()

    def scale_source_image(self):
        w, h = self.source.width(),self.source.height()
        self.source_image = self.source_image.resize((int(w * self.scale), int(h * self.scale)))
        self.source = ImageTk.PhotoImage(self.source_image,  master = self.master)
        w, h = self.source.width(),self.source.height()

        w, h = self.trimap.width(),self.trimap.height()
        self.trimap_image = self.trimap_image.resize((int(w * self.scale), int(h * self.scale)))
        self.trimap = ImageTk.PhotoImage(self.trimap_image,  master = self.master)
        w, h = self.trimap.width(),self.trimap.height()
        self.canvas_1.config(width = self.canvas_shape, height = h)
        self.canvas_2.config(width = self.canvas_shape, height = h)
        self.canvas_1.create_image((self.canvas_shape//2, h//2), image = self.source, anchor = tk.CENTER)
        self.canvas_2.create_image((self.canvas_shape//2, h//2), image = self.trimap, anchor = tk.CENTER)

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

    def choose_target_image(self):
        image_name = fido.askopenfilename(title = "Target image")
        if image_name:
            self.target_image = Image.open(image_name)
            self.target = ImageTk.PhotoImage(self.target_image,  master = self.master)
            w, h = self.target.width(),self.target.height()
            self.canvas1.config(width = w, height = h)
            self.canvas1.create_image((0,0), image = self.target, anchor = tk.NW)
            self.load_target_image = True

    def choose_trimap_image(self):
        image_name = fido.askopenfilename(title = "Trimap image")
        if image_name:
            self.trimap_image = Image.open(image_name).convert('RGB')
            self.trimap = ImageTk.PhotoImage(self.trimap_image,  master = self.master)
            w, h = self.trimap.width(),self.trimap.height()
            self.canvas_2.config(width = self.canvas_shape, height = h)
            self.canvas_2.create_image((self.canvas_shape//2, h//2), image = self.trimap, anchor = tk.CENTER)
            self.load_trimap_image = True

    def choose_source_image(self):
        image_name = fido.askopenfilename(title = "Source image")
        if image_name:
            self.source_image = Image.open(image_name)
            self.source = ImageTk.PhotoImage(self.source_image,  master = self.master)
            w, h = self.source.width(),self.source.height()
            self.canvas_1.config(width = self.canvas_shape, height = h)
            self.canvas_1.create_image((self.canvas_shape//2, h//2), image = self.source, anchor = tk.CENTER)
            self.load_source_image = True

    def show_clonning(self):
        self.result_ = ImageTk.PhotoImage(self.result,  master = self.master)
        self.canvas1.create_image((0,0), image = self.result_, anchor = tk.NW)

    def done(self):
        if self.load_target_image and self.load_source_image and self.load_trimap_image:
            w, h = self.target.width(),self.target.height()
        self.result = self.matting( (w//2, h//2), self.mode)
        self.show_clonning()
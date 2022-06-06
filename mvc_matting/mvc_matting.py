import tkinter as tk
from tkinter import filedialog as fido
from PIL import ImageTk, Image
from cloning import Cloning
import numpy as np

class GUI(Cloning):

    def __init__(self, title = "Image Loader"):
        
        super().__init__()
        self.master = tk.Tk()
        self.master.withdraw()
        self.master.title(title)

        self.canvas = tk.Frame(self.master)
        self.canvas.grid(row = 1, column = 0)

        self.canvas_1 = tk.Canvas(self.canvas)
        self.canvas_1.pack(fill='x')
        self.canvas_2 = tk.Canvas(self.canvas)
        self.canvas_2.pack(fill='x')

        self.source_image_button = tk.Frame(self.master)
        self.source_image_button.grid(row = 2, column = 0, sticky = tk.NSEW)

        self.image_button1 = tk.Button(self.source_image_button, font = "Helvetica 12",text = "Choose Source Image", command = self.choose_source_image)
        self.image_button1.pack(fill='x')
        self.image_button2 = tk.Button(self.source_image_button, font = "Helvetica 12",text = "Choose Trimap Image", command = self.choose_trimap_image)
        self.image_button2.pack(fill='x')

        self.settingButtons = tk.Frame(self.master)
        self.settingButtons.grid(row = 0, column = 0)

        self.QuickStart = tk.Button(self.master, font = "Helvetica 12",text = "QuickStart", command = self.QuickStart)
        self.QuickStart.grid(row = 0, column = 1)

        self.image_button = tk.Button(self.master, font = "Helvetica 12",text = "Choose Target Image", command = self.choose_target_image)
        self.image_button.grid(row = 2, column = 1, sticky = tk.NSEW)
        self.canvas1 = tk.Canvas(self.master)
        self.canvas1.grid(row = 1, column = 1)

        self.button = tk.Button(self.settingButtons, font = "Helvetica 12", text = "Matting", command = self.done)

        self.button.pack(side=tk.LEFT)
        self.master.update()
        self.master.resizable(True, True)
        self.master.deiconify()
        self.canvas1.bind("<Button-1>", self.target_click)

    def QuickStart(self):
        target = "../image/background.jpeg"
        source = "../image/input.png"
        trimap = "../image/trimap.png"
        self.source_image = Image.open(source)
        self.source = ImageTk.PhotoImage(self.source_image,  master = self.master)
        w, h = self.source.width(),self.source.height()
        self.canvas_1.config(width = w, height = h)
        self.canvas_1.create_image((0,0), image = self.source, anchor = tk.NW)
    
        self.trimap_image = Image.open(trimap)
        self.trimap = ImageTk.PhotoImage(self.trimap_image,  master = self.master)
        w, h = self.trimap.width(),self.trimap.height()
        self.canvas_2.config(width = w, height = h)
        self.canvas_2.create_image((0,0), image = self.trimap, anchor = tk.NW)

        self.target_image = Image.open(target)
        self.target = ImageTk.PhotoImage(self.target_image,  master = self.master)
        w, h = self.target.width(),self.target.height()
        self.canvas1.config(width = w, height = h)
        self.canvas1.create_image((0,0), image = self.target, anchor = tk.NW)


    def target_click(self, event):
        print ("[target] clicked at", event.x, event.y)
        self.result = self.matting(( event.x, event.y))
        self.show_clonning()

    def choose_target_image(self):
        image_name = fido.askopenfilename(title = "Target image")
        if image_name:
            self.target_image = Image.open(image_name).convert('RGB')
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
            self.canvas_2.config(width = w, height = h)
            self.canvas_2.create_image((0,0), image = self.trimap, anchor = tk.NW)

    def choose_source_image(self):
        image_name = fido.askopenfilename(title = "Source image")
        if image_name:
            self.source_image = Image.open(image_name).convert('RGB')
            self.source = ImageTk.PhotoImage(self.source_image,  master = self.master)
            w, h = self.source.width(),self.source.height()
            self.canvas_1.config(width = w, height = h)
            self.canvas_1.create_image((0,0), image = self.source, anchor = tk.NW)
            self.load_source_image = True

    def show_clonning(self):
        self.result_ = ImageTk.PhotoImage(self.result,  master = self.master)
        self.canvas1.create_image((0,0), image = self.result_, anchor = tk.NW)

    def done(self):
        w, h = self.target.width(),self.target.height()
        self.result = self.matting( (w//2, h//2))
        self.show_clonning()


if __name__ == "__main__":
    loader = GUI()
    loader.master.mainloop()

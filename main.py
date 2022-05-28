import tkinter as tk
from tkinter import filedialog as fido
from PIL import ImageTk, Image
import numpy as np
import cv2 as cv


class CanvasImage:

    def __init__(self, title = "Image Loader"):

        self.master = tk.Tk()
        self.master.withdraw()
        self.master.title(title)
        self.canvas = tk.Canvas(self.master)
        self.canvas.grid(row = 1, column = 0)

        self.image_button = tk.Button(self.master, font = "Helvetica 12",text = "Choose Source Image", command = self.choose_source_image)
        self.image_button.grid(row = 2, column = 0, sticky = tk.NSEW)

        self.settingButtons = tk.Frame(self.master)
        self.settingButtons.grid(row = 0, column = 0)

        self.image_button = tk.Button(self.master, font = "Helvetica 12",text = "Choose Target Image", command = self.choose_target_image)
        self.image_button.grid(row = 2, column = 1, sticky = tk.NSEW)
        self.canvas1 = tk.Canvas(self.master)
        self.canvas1.grid(row = 1, column = 1)

        self.button1 = tk.Button(self.settingButtons, font = "Helvetica 12",text = "Undo", command = self.undo)
        self.button2 = tk.Button(self.settingButtons, font = "Helvetica 12",text = "Clear", command = self.clear)
        self.button3 = tk.Button(self.settingButtons, font = "Helvetica 12", text = "Done", command = self.done)

        self.button1.pack(side=tk.LEFT)
        self.button2.pack(side=tk.LEFT)
        self.button3.pack(side=tk.LEFT)

        self.master.update()
        self.master.resizable(True, True)
        self.master.deiconify()

        self.canvas.bind("<Button-1>", self.click)
        self.pts = []
        self.line = []
        self.load_source_image = False
        self.load_target_image = False

    def click(self,event):
        
        if self.load_source_image == False:
            return

        print ("[source] clicked at", event.x, event.y)
        if len(self.pts) == 0:
            x1, y1 = ( event.x - 1 ), ( event.y - 1 )
            x2, y2 = ( event.x + 1 ), ( event.y + 1 )
            self.line.append(self.canvas.create_oval( x1, y1, x2, y2, fill = "red", width=1 ))
            self.pts.append([event.x, event.y])
            return

        x1 = self.pts[-1][0]
        y1 = self.pts[-1][1]
        x2 = event.x
        y2 = event.y
        self.pts.append([event.x, event.y])
        self.line.append(self.canvas.create_line(x1,y1,x2,y2,fill="red", width=1))

    def choose_target_image(self):
        image_name = fido.askopenfilename(title = "Target image")
        if image_name:
            img = Image.open(image_name)
            self.target = ImageTk.PhotoImage(img,  master = self.master)
            w, h = self.target.width(),self.target.height()
            self.canvas1.config(width = w, height = h)
            self.canvas1.create_image((0,0), image = self.target, anchor = tk.NW)
            self.load_target_image = True

    def choose_source_image(self):
        image_name = fido.askopenfilename(title = "Source image")
        if image_name:
            self.source_image = Image.open(image_name)
            self.source = ImageTk.PhotoImage(self.source_image,  master = self.master)
            w, h = self.source.width(),self.source.height()
            self.canvas.config(width = w, height = h)
            self.canvas.create_image((0,0), image = self.source, anchor = tk.NW)
            self.load_source_image = True

    def clear(self):
        if len(self.line) != 0: 
            self.canvas.delete('all')
            self.pts = []
            w, h = self.source.width(),self.source.height()
            self.canvas.config(width = w, height = h)
            self.canvas.create_image((0,0), image = self.source, anchor = tk.NW)
        
    def undo(self):
        if len(self.line) != 0: 
            self.canvas.delete(self.line.pop())
            self.pts.pop()
        
    def done(self):
        if len(self.line) == 0: 
            return

        self.line.append(self.canvas.create_line(self.pts[-1][0], self.pts[-1][1], self.pts[0][0], self.pts[0][1],fill="red", width=1))
        self.pts.append(self.pts[0])

        mask = np.zeros_like(self.source_image)
        cv.fillPoly(mask, [np.array(self.pts).reshape((-1, 1, 2))], (1, 1, 1))
        mask[[p[1] for p in self.pts], [p[0] for p in self.pts], :] = 0
        self.source_image =  Image.fromarray (mask * self.source_image)
        self.source_image.show()



if __name__ == "__main__":
    loader = CanvasImage()
    loader.master.mainloop()

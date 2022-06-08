import tkinter as tk
from tkinter import filedialog as fido
from PIL import ImageTk, Image
from cloning import Cloning
import numpy as np

class GUI(Cloning):

    def __init__(self, title = "Image Loader", mode = "cv2"):

        self.master = tk.Tk()
        self.master.withdraw()
        self.master.title(title)
        self.canvas = tk.Canvas(self.master)
        self.canvas.grid(row = 1, column = 0)

        self.image_button = tk.Button(self.master, font = "Helvetica 12",text = "Choose Source Image", command = self.choose_source_image)
        self.image_button.grid(row = 2, column = 0, sticky = tk.NSEW)

        self.settingButtons = tk.Frame(self.master)
        self.settingButtons.grid(row = 0, column = 0)

        self.QuickStart = tk.Button(self.master, font = "Helvetica 12",text = "QuickStart", command = self.QuickStart)
        self.QuickStart.grid(row = 0, column = 1)

        self.image_button = tk.Button(self.master, font = "Helvetica 12",text = "Choose Target Image", command = self.choose_target_image)
        self.image_button.grid(row = 2, column = 1, sticky = tk.NSEW)
        self.canvas1 = tk.Canvas(self.master)
        self.canvas1.grid(row = 1, column = 1)

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
        

        self.master.update()
        self.master.resizable(True, True)
        self.master.deiconify()

        self.canvas.bind("<Button-1>", self.source_click)
        self.canvas1.bind("<Button-1>", self.target_click)
        self.line = []
        self.load_source_image = False
        self.load_target_image = False

        self.mode = mode
        self.scale = 1

    def QuickStart(self):
        target = "image/target.jpeg"
        source = "image/source.jpeg"
        self.source_image = Image.open(source)
        self.source = ImageTk.PhotoImage(self.source_image,  master = self.master)
        w, h = self.source.width(),self.source.height()
        self.canvas.config(width = w, height = h)
        self.canvas.create_image((0,0), image = self.source, anchor = tk.NW)
        self.load_source_image = True

        self.target_image = Image.open(target)
        self.target = ImageTk.PhotoImage(self.target_image,  master = self.master)
        w, h = self.target.width(),self.target.height()
        self.canvas1.config(width = w, height = h)
        self.canvas1.create_image((0,0), image = self.target, anchor = tk.NW)
        self.load_target_image = True
        self.pts = np.load('border.npy')

        for i in range(len(self.pts)-1):
            self.line.append(self.canvas.create_line(self.pts[i][0], self.pts[i][1], self.pts[i+1][0], self.pts[i+1][1],fill="red", width=1))

    def image_cloniing(self, center):
        if self.mode == "cv2":
            result = self.OpenCV_Cloning(center)
        elif self.mode == "mvc":
            result = self.seamlessClone(center)
        else:
            result = self.seamlessClone_mesh(center)
        return result

    def zoom_in(self):
        if self.load_source_image and self.scale <= 1.3:
            w, h = self.source.width(),self.source.height()
            self.scale = 1.05
            self.source_image = self.source_image.resize((int(w * self.scale), int(h * self.scale)))
            self.source = ImageTk.PhotoImage(self.source_image,  master = self.master)
            w, h = self.source.width(),self.source.height()
            self.canvas.config(width = w, height = h)
            self.canvas.create_image((0,0), image = self.source, anchor = tk.NW)

            # if len(self.pts) != 0:
            #     self.pts = self.pts * self.scale
            #     for i in range(len(self.pts)-1):
            #         self.line.append(self.canvas.create_line(self.pts[i][0], self.pts[i][1], self.pts[i+1][0], self.pts[i+1][1],fill="red", width=1))

    def zoom_out(self):
        if self.load_source_image and self.scale >= 0.5:
            w, h = self.source.width(),self.source.height()
            self.scale = 0.95
            self.source_image = self.source_image.resize((int(w * self.scale), int(h * self.scale)))
            self.source = ImageTk.PhotoImage(self.source_image,  master = self.master)
            w, h = self.source.width(),self.source.height()
            self.canvas.config(width = w, height = h)
            self.canvas.create_image((0,0), image = self.source, anchor = tk.NW)

    def target_click(self, event):
        print ("[target] clicked at", event.x, event.y)
        if self.mode == "cv2":
            if event.x - self.source.width()//2 < 0 or event.x + self.source.width()//2 > self.target.width() or \
            event.y - self.source.height()//2  < 0 or event.y + self.source.height()//2 > self.target.height():
                print("position out of range")
                return
        self.result = self.image_cloniing(np.array([event.x, event.y]))
        self.show_clonning()
        
    def source_click(self,event):
        
        if self.load_source_image == False:
            return

        print ("[source] clicked at", event.x, event.y)
        if len(self.pts) == 0:
            x1, y1 = ( event.x - 1 ), ( event.y - 1 )
            x2, y2 = ( event.x + 1 ), ( event.y + 1 )
            self.line.append(self.canvas.create_oval( x1, y1, x2, y2, fill = "red", width=1 ))
            self.pts = np.vstack((self.pts, [event.x, event.y]))
            # self.pts.append([event.x, event.y])
            return

        x1 = self.pts[-1][0]
        y1 = self.pts[-1][1]
        x2 = event.x
        y2 = event.y
        self.pts = np.vstack((self.pts, [event.x, event.y]))
        # self.pts.append([event.x, event.y])
        self.line.append(self.canvas.create_line(x1,y1,x2,y2,fill="red", width=1))

    def choose_target_image(self):
        image_name = fido.askopenfilename(title = "Target image")
        if image_name:
            self.target_image = Image.open(image_name)
            self.target = ImageTk.PhotoImage(self.target_image,  master = self.master)
            w, h = self.target.width(),self.target.height()
            self.canvas1.config(width = w, height = h)
            self.canvas1.create_image((0,0), image = self.target, anchor = tk.NW)
            self.load_target_image = True

    def show_clonning(self):
        self.result = Image.fromarray(self.result)
        self.result = ImageTk.PhotoImage(self.result,  master = self.master)
        self.canvas1.create_image((0,0), image = self.result, anchor = tk.NW)

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
            self.line = []
            self.pts = np.empty((0, 2))
            w, h = self.source.width(),self.source.height()
            self.canvas.config(width = w, height = h)
            self.canvas.create_image((0,0), image = self.source, anchor = tk.NW)
        
    def undo(self):
        if len(self.line) != 0: 
            self.canvas.delete(self.line.pop())
            if len(self.pts) != 0:
                self.pts = self.pts[:-1]
        
    def done(self):
        if len(self.line) <= 3: 
            return

        self.line.append(self.canvas.create_line(self.pts[-1][0], self.pts[-1][1], self.pts[0][0], self.pts[0][1],fill="red", width=1))
        # self.pts.append(self.pts[0])
        self.pts = np.vstack((self.pts, self.pts[0]))
        
        # np.save('border', self.pts)
        w, h = self.target.width(),self.target.height()

        # Clonning
        self.result = self.image_cloniing(np.array([w//2, h//2]))
        self.show_clonning()

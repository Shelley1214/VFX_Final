import tkinter as tk
from tkinter import filedialog as fido
from PIL import ImageTk, Image
import cv2
from cloning import Cloning
import numpy as np
from video_track import video_track

class GUI_video():

    def __init__(self, title = "Image Loader", mode = "cv2"):

        self.master = tk.Tk()
        self.master.withdraw()
        self.master.title(title)
        self.canvas = tk.Canvas(self.master)
        self.canvas.grid(row = 1, column = 0)
        self.canvas_shape = 600

        self.image_button = tk.Button(self.master, font = "Helvetica 12",text = "Choose Source Image", command = self.choose_source_image)
        self.image_button.grid(row = 2, column = 0, sticky = tk.NSEW)

        self.settingButtons = tk.Frame(self.master)
        self.settingButtons.grid(row = 0, column = 0)

        self.QuickStart = tk.Button(self.master, font = "Helvetica 12",text = "QuickStart", command = self.QuickStart)
        self.QuickStart.grid(row = 0, column = 1)
        self.GenerateVideo = tk.Button(self.master, font = "Helvetica 12",text = "Generate Video", command = self.GenerateVideo)
        self.GenerateVideo.grid(row = 0, column = 1, sticky = tk.W)

        self.image_button = tk.Button(self.master, font = "Helvetica 12",text = "Choose Target Video", command = self.choose_target_image)
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
        self.load_target_video = False

        self.mode = mode
        self.scale = 1
        
        self.video_name = ""
        self.source_image = []
        self.target_image = []
        self.pts = np.empty((0, 2), dtype=int)
        self.cx = 0
        self.cy = 0

    def QuickStart(self):
        target_video = "image/Bear_orig.avi"
        cap = cv2.VideoCapture(target_video)
        _ , target = cap.read()
        cv2.imwrite("image/target_video.jpeg", target)
        cap.release()
        self.video_name = "image/Bear_orig.avi"
        target = "image/target_video.jpeg"
        source = "image/source.jpeg"
        self.source_image = Image.open(source)
        self.source = ImageTk.PhotoImage(self.source_image,  master = self.master)
        sw, sh = self.source.width(),self.source.height()
        self.canvas.config(width = self.canvas_shape, height = sh)
        self.canvas.create_image((self.canvas_shape//2, sh//2), image = self.source, anchor = tk.CENTER)
        self.load_source_image = True

        self.target_image = Image.open(target)
        self.target = ImageTk.PhotoImage(self.target_image,  master = self.master)
        tw, th = self.target.width(),self.target.height()
        self.canvas1.config(width = tw, height = th)
        self.canvas1.create_image((0,0), image = self.target, anchor = tk.NW)
        self.load_target_image = True
        self.pts = np.load('border.npy')

        for i in range(len(self.pts)-1):
            offset = self.canvas_shape // 2 - sw // 2
            points = [self.pts[i][0] + offset, self.pts[i][1], self.pts[i+1][0] + offset, self.pts[i+1][1]]
            self.line.append(self.canvas.create_line(points[0], points[1], points[2], points[3], fill="red", width=1))

    def image_cloniing(self, center):
        clone = Cloning(self.source_image, self.target_image, self.pts)
        if self.mode == "cv2":
            result = clone.OpenCV_Cloning(center)
        elif self.mode == "mvc":
            result = clone.seamlessClone(center)
        else:
            result = clone.seamlessClone_mesh(center)
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
            self.scale_source_image()

    def zoom_out(self):
        if self.load_source_image:
            self.scale = 0.95
            self.scale_source_image()

    def target_click(self, event):
        print ("[target] clicked at", event.x, event.y)
        if self.mode == "cv2":
            if event.x - self.source.width()//2 < 0 or event.x + self.source.width()//2 > self.target.width() or \
            event.y - self.source.height()//2  < 0 or event.y + self.source.height()//2 > self.target.height():
                print("position out of range")
                return
        self.result = self.image_cloniing(np.array([event.x, event.y]))
        self.show_clonning()
        self.cx = event.x
        self.cy = event.y
        
    def source_click(self,event):
        
        if self.load_source_image == False:
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
        video_name = fido.askopenfilename(title = "Target video")
        if video_name:
            cap = cv2.VideoCapture(video_name)
            _ , frame = cap.read()
            cv2.imwrite("image/target_video_frame.jpeg", frame)
            cap.release()
            image_name = "image/target_video_frame.jpeg"
            self.video_name = video_name
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
        if len(self.line) <= 3: 
            return
        
        w = self.source.width()
        offset = self.canvas_shape // 2 - w // 2
        self.line.append(self.canvas.create_line(self.pts[-1][0] + offset, self.pts[-1][1], self.pts[0][0] + offset, self.pts[0][1],fill="red", width=1))
        self.pts = np.vstack((self.pts, self.pts[0]))
        
        # np.save('border', self.pts)
        w, h = self.target.width(),self.target.height()

        # Clonning
        self.result = self.image_cloniing(np.array([w//2, h//2]))
        self.show_clonning()
    
    def show_clonning_video(self):
        cap = cv2.VideoCapture('output.avi')
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Video End.")
                break
            cv2.imshow('Output Video', frame)
            if cv2.waitKey(10) == ord('q'):
                break
    
    def GenerateVideo(self):
        video_track(np.array(self.source_image), self.pts, self.video_name,(self.cx, self.cy), self.mode)
        self.show_clonning_video()
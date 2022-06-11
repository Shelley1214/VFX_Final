import tkinter as tk
from tkinter import ttk
from gui import GUI
from gui_video import GUI_video
from gui_matting import GUI_matting
# import argparse

class Merge_GUI():

    def __init__(self, title = "Image Loader"):
        
        self.master = tk.Tk()
        style = ttk.Style(self.master)
        self.master.call('source', 'azure.tcl')
        self.master.tk.call("set_theme", "dark")

        self.master.withdraw()
        self.master.title(title)
        self.tabControl = ttk.Notebook(self.master)

        # Cloning
        self.tab1 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text='Cloning') 
        self.cloning = GUI(self.tab1)

        # Matting
        self.tab2 = ttk.Frame(self.tabControl) 
        self.tabControl.add(self.tab2, text='Matting')
        self.matting = GUI_matting(self.tab2)

        #Video
        self.tab3 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab3, text='Video')
        self.tabControl.pack(expand=1, fill="both")
        self.video = GUI_video(self.tab3)


        self.master.update()
        self.master.resizable(True, True)
        self.master.deiconify()
        self.master.geometry('{0}x{1}+0+0'.format(self.master.winfo_screenwidth(), self.master.winfo_screenheight()-200))

        # self.tabControl.bind("<ButtonRelease-1>", self.TabChanged)
        # def TabChanged(self,event=None):
            # event.widget.tab('current')['text'] == "Matting":
            # pass


# def parse_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "--mode", 
#         "-m", 
#         type=str,
#         choices=["cv2", "mvc", "mesh"],
#         default="mesh",
#     )

#     parser.add_argument("-v", "--video", action='store_true')
#     args = parser.parse_args()
#     return args


if __name__ == "__main__":
    # args = parse_args()
    # loader = Merge_GUI(mode=args.mode)
    loader = Merge_GUI()
    loader.master.mainloop()


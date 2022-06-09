from gui import GUI
from gui_video import GUI_video
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", 
        "-m", 
        type=str,
        choices=["cv2", "mvc", "mesh"],
        default="mesh",
    )

    parser.add_argument("-v", "--video", action='store_true')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    if args.video:
        loader = GUI_video(mode = args.mode)
    else:
        loader = GUI(mode=args.mode)
    loader.master.mainloop()


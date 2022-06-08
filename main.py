from gui import GUI
from videoTrack import img_load, video_track
import argparse
import cv2

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", 
        "-m", 
        type=str,
        choices=["cv2", "mvc", "mesh"],
        default="cv2",
    )
    parser.add_argument(
        "--img_file",
        type=str,
        help="Path of the image.",
        default="./image/dog.jpg",
    )
    
    parser.add_argument(
        "--video_file",
        type=str,
        help="Path of the video.",
        default="./video/Bear_orig.avi",
    )


    parser.add_argument("-v", "--video", action='store_true')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    if args.video:
        img = img_load(args.img_file)
        
        video_track(args.video_file)
    else:
        loader = GUI(mode=args.mode)
        loader.master.mainloop()


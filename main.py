from gui import GUI
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
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    loader = GUI(mode=args.mode)
    loader.master.mainloop()

import argparse
import os
import c3d
from pxr import Usd, UsdSkel
import numpy as np
import matplotlib.pyplot as plt

def dir_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("path_c3d", type=dir_path, help="Input path for c3d file.")
    parser.add_argument("path_usd", type=dir_path, help="Input path for usd file.")
    parser.add_argument("-o", "--output", type=str)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    #loading c3d file
    reader = c3d.Reader(open(args.path_c3d, "rb"))
    points_c3d = np.array([points[:, :3] for _, points, _ in reader.read_frames()])
    points_c3d_shift = np.array([[np.linalg.norm(points_c3d[i, j] - points_c3d[i - 1, j]) for j in range(points_c3d.shape[1])] for i in range(1, len(points_c3d))])
    print(points_c3d_shift)
    print(f"{points_c3d_shift.shape[0]=}")
    plt.plot(points_c3d_shift)
    plt.show()

    #loading usd file
    stage = Usd.Stage.Open(args.path_usd)
    anim_prim = stage.GetPrimAtPath("/A1/Skeleton/Anim")
    animation = UsdSkel.Animation(anim_prim)
    translations = np.array([animation.GetTranslationsAttr().Get(Usd.TimeCode(i)) for i in range(int(animation.GetTranslationsAttr().GetNumTimeSamples()))])
    rotations = np.array([animation.GetRotationsAttr().Get(Usd.TimeCode(i)) for i in range(int(animation.GetRotationsAttr().GetNumTimeSamples()))])

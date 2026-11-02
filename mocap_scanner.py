import argparse
import os
import c3d
from pxr import Usd, UsdSkel, UsdGeom
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


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

def load_c3d(c3d_file_path):
    reader = c3d.Reader(open(c3d_file_path, "rb"))
    points = np.array([points[:, :3] for _, points, _ in reader.read_frames()])
    labels = [label.split(":")[1] for label in reader.point_labels]
    return points, labels

def load_usd_to_3d(usd_file_path):
    stage = Usd.Stage.Open(usd_file_path)
    skeleton = UsdSkel.Skeleton(stage.GetPrimAtPath("/A1/Skeleton"))

    skel_root = UsdSkel.Root(stage.GetPrimAtPath("/A1"))
    if not skel_root:
        raise ValueError("/A1 is not a valid UsdSkelRoot")

    cache = UsdSkel.Cache()
    cache.Populate(skel_root, Usd._PrimFlagsPredicate.Tautology())
    skel_query = cache.GetSkelQuery(skeleton)

    frame = 10
    xform_cache = UsdGeom.XformCache(Usd.TimeCode(frame))
    joint_world_transforms = skel_query.ComputeJointWorldTransforms(xform_cache)

    joint_labels = [str(joint) for joint in skel_query.GetJointOrder()]
    joint_points = np.array([
        tuple(transform.ExtractTranslation())
        for transform in joint_world_transforms
    ])

    return joint_points, joint_labels

if __name__ == "__main__":
    args = parse_arguments()

    #loading c3d file
    points_c3d , labels_c3d = load_c3d(args.path_c3d)
    points_c3d_shift = np.array([[np.linalg.norm(points_c3d[i, j] - points_c3d[i - 1, j]) for j in range(points_c3d.shape[1])] for i in range(1, len(points_c3d))])

    #loading usd file
    points_usd, labels_usd = load_usd_to_3d(args.path_usd)
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
    # stage = Usd.Stage.Open(args.path_usd)
    # anim_prim = stage.GetPrimAtPath("/A1/Skeleton/Anim")
    # animation = UsdSkel.Animation(anim_prim)
    # translations = np.array([animation.GetTranslationsAttr().Get(Usd.TimeCode(i)) for i in range(int(animation.GetTranslationsAttr().GetNumTimeSamples()))])
    # rotations = np.array([animation.GetRotationsAttr().Get(Usd.TimeCode(i)) for i in range(int(animation.GetRotationsAttr().GetNumTimeSamples()))])
    # translations_shift = np.array([[np.linalg.norm(translations[i, j] - translations[i - 1, j]) for j in range(translations.shape[1])] for i in range(1, len(translations))])
    # rotation_differences = rotations[1:] - rotations[:-1]
    # rotation_sums = rotations[1:] + rotations[:-1]
    # rotations_shift = np.minimum(
    #     np.linalg.norm(rotation_differences, axis=-1),
    #     np.linalg.norm(rotation_sums, axis=-1),
    # )

    points_usd, labels_usd = load_usd_to_3d(args.path_usd)

    # plt.plot(translations_shift)
    # plt.title("Translations shift")
    # plt.show()
    # plt.plot(rotations_shift)
    # plt.title("Rotations shift")
    # plt.show()

    #detecting outliers in c3d file
    # q3_c3d = np.percentile(points_c3d_shift.flatten(), 75, axis=0)
    # q1_c3d = np.percentile(points_c3d_shift.flatten(), 25, axis=0)
    # iqr_c3d = q3_c3d - q1_c3d

    # upper_bound_c3d = q3_c3d + 1.5 * iqr_c3d
    # outliers_c3d = np.where(points_c3d_shift > upper_bound_c3d)
    z = np.abs(stats.zscore(points_c3d_shift))
    threshold = 4
    outliers_c3d = np.where(z > threshold)
    print(f"Upper bound: {z}\nOutliers in c3d file: {outliers_c3d}")
    print(points_c3d_shift)
    print(f"{points_c3d_shift.shape[0]=}")
    plt.plot(points_c3d_shift)
    plt.show()
import sys
import cv2
import os
from sys import platform
import argparse
import time
import math
import json

poses = {
    'left_elbow': (5, 6, 7),
    'left_hand': (1, 5, 7),
    'left_knee': (12, 13, 14),
    'left_ankle': (5, 12, 14),
    'right_elbow': (2, 3, 4),
    'right_hand': (1, 2, 4),
    'right_knee': (9, 10, 11),
    'right_ankle': (2, 9, 11)
}

def angle_between_points(p0, p1, p2):
    # 计算角度
    a = (p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2
    b = (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2
    c = (p2[0] - p0[0]) ** 2 + (p2[1] - p0[1]) ** 2
    if a * b == 0:
        return -1.0

    return math.acos((a + b - c) / math.sqrt(4 * a * b)) * 180 / math.pi


def get_angle_point(human, pos):
    # 返回构成各部位的三个点坐标
    pnts = []

    if pos in poses:
        pos_list = poses[pos]
    else:
        print('Unknown  [%s]', pos)
        return pnts

    for i in range(3):
        if human[pos_list[i]][2] <= 0.1:
            # print('component [%d] incomplete' % (pos_list[i]))
            return pnts
        pnts.append((int(human[pos_list[i]][0]), int(human[pos_list[i]][1])))
    return pnts

def cal_angle(human,pos):
    pnts = get_angle_point(human, pos)
    if len(pnts) != 3:
        # print('component incomplete')
        return -1
    angle = 0
    if pnts is not None:
        angle = angle_between_points(pnts[0], pnts[1], pnts[2])
    return angle


def main_angle(imagePath,params):
    try:
        # Import Openpose (Windows/Ubuntu/OSX)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        try:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            # 改成openpose的安装位置，如“/usr/local/python”
            # sys.path.append('/usr/local/python')
            sys.path.append('./build/python/')
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
        except ImportError as e:
            print(
                'Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
            raise e

        # Flags
        parser = argparse.ArgumentParser()
        parser.add_argument("--no_display", default=False, help="Enable to disable the visual display.")
        args = parser.parse_known_args()

        # Custom Params (refer to include/openpose/flags.hpp for more parameters)


        # Add others in path?
        for i in range(0, len(args[1])):
            curr_item = args[1][i]
            if i != len(args[1]) - 1:
                next_item = args[1][i + 1]
            else:
                next_item = "1"
            if "--" in curr_item and "--" in next_item:
                key = curr_item.replace('-', '')
                if key not in params:  params[key] = "1"
            elif "--" in curr_item and "--" not in next_item:
                key = curr_item.replace('-', '')
                if key not in params: params[key] = next_item

        # Starting OpenPose

        file_name = imagePath.split('/')[-1].split('.')[0]
        opWrapper = op.WrapperPython()
        opWrapper.configure(params)
        opWrapper.start()
        datum = op.Datum()
        imageToProcess = cv2.imread(imagePath)
        datum.cvInputData = imageToProcess
        opWrapper.emplaceAndPop(op.VectorDatum([datum]))

        # print("Body keypoints: \n" + str(datum.poseKeypoints))


        # human_count = len(datum.poseKeypoints)

        # for i in range(human_count):
        #     for j in range(25):
        #         print(datum.poseKeypoints[i][j][0])
        # 只针对图像中出现单目标的情况
        anses = {}
        # for i in range(human_count):
        ans = {}
        for pos in poses:
            ans[pos]=cal_angle(datum.poseKeypoints[0],pos)
        # anses[i]=ans
        data = json.loads(json.dumps(ans))
        # data = json.loads(json.dumps(anses))

        with open("result" + '/' + "{}.".format(file_name)+"_angle.json", 'w', encoding='utf-8') as file:
            file.write(json.dumps(data, indent=2, ensure_ascii=False))

        if not args[0].no_display:
            # cv2.imshow("OpenPose 1.7.0 - Tutorial Python API", datum.cvOutputData)
            cv2.imwrite("result" + '/' + "{}.jpg".format(file_name), datum.cvOutputData)
            # key = cv2.waitKey(15)
        return ans

        # Read frames on directory
        # imagePaths = op.get_images_on_directory(args[0].image_dir);

        # Process and display images
        # for imagePath in imagePaths:
        #     print(imagePath)
        #     file_name = imagePath.split('.')[0].split('/')[-1]
        #     datum = op.Datum()
        #     imageToProcess = cv2.imread(imagePath)
        #     datum.cvInputData = imageToProcess
        #     opWrapper.emplaceAndPop(op.VectorDatum([datum]))
        #
        #     print("Body keypoints: \n" + str(datum.poseKeypoints))
        #
        #
        #     human_count = len(datum.poseKeypoints)
        #
        #     # for i in range(human_count):
        #     #     for j in range(25):
        #     #         print(datum.poseKeypoints[i][j][0])
        #     anses = {}
        #     for i in range(human_count):
        #         ans = {}
        #         for pos in poses:
        #             ans[pos]=cal_angle(datum.poseKeypoints[i],pos)
        #         anses[i]=ans
        #
        #     data = json.loads(json.dumps(anses))
        #
        #     with open("result" + '/' + "{}.".format(file_name)+"_angle.json", 'w', encoding='utf-8') as file:
        #         file.write(json.dumps(data, indent=2, ensure_ascii=False))
        #
        #     if not args[0].no_display:
        #         cv2.imshow("OpenPose 1.7.0 - Tutorial Python API", datum.cvOutputData)
        #         cv2.imwrite("result" + '/' + "{}.jpg".format(file_name), datum.cvOutputData)
        #         key = cv2.waitKey(15)
        #         if key == 27: break

    except Exception as e:
        print(e)
        sys.exit(-1)

# if __name__ == "__main__":
#     main_angle()

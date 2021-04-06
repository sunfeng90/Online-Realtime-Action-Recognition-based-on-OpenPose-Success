# -*- coding: UTF-8 -*-
## 采集某个视频或者动作中的数据s
import cv2 as cv
import csv as csv
import argparse
import numpy as np
import time
from Utils.utils import get_action_code, choose_run_mode, load_pretrain_model, set_video_writer
from Pose.pose_visualizer import TfPoseVisualizer
from Action.recognizer import load_action_premodel, framewise_recognize

parser = argparse.ArgumentParser(description='Action Recognition by OpenPose')
parser.add_argument('--video', help='Path to video file.')
parser.add_argument('--type', help='Train action type like run, jump, and so on.')
args = parser.parse_args()


# 导入相关模型
estimator = load_pretrain_model('VGG_origin')
action_classifier = load_action_premodel('Action/framewise_recognition.h5')

# 参数初始化
realtime_fps = '0.0000'
start_time = time.time()
fps_interval = 1
fps_count = 0
run_timer = 0
frame_count = 0

# 读写视频文件（仅测试过webcam输入）
cap = choose_run_mode(args)
video_writer = set_video_writer(cap, write_fps=int(7.0))

# # 保存关节数据的csv文件，用于训练过程(for training)
f = open('Data/origin_data.txt', 'a+', encoding='utf-8', newline='')
writer = csv.writer(f)
# 每个关节点名称
f_headers = ['nose_x', 'nose_y', 'neck_x', 'neck_y', 'Rshoulder_x', 'Rshoulder_y',
             'Relbow_x', 'Relbow_y', 'Rwrist_x', 'RWrist_y', 'LShoulder_x', 'LShoulder_y',
             'LElbow_x', 'LElbow_y', 'LWrist_x', 'LWrist_y', 'RHip_x', 'RHip_y', 'RKnee_x',
             'RKnee_y', 'RAnkle_x', 'RAnkle_y', 'LHip_x', 'LHip_y', 'LKnee_x', 'LKnee_y',
             'LAnkle_x', 'LAnkle_y', 'REye_x', 'REye_y', 'LEye_x', 'LEye_y', 'REar_x',
             'REar_y', 'LEar_x', 'LEar_y', 'class']
writer.writerow(f_headers)

if not args.type:
    print('请输入具体采集的动作类型:-<')
else:
    while cv.waitKey(1) < 0:
       has_frame, show = cap.read()
       if has_frame:
            fps_count += 1
            frame_count += 1

            # pose estimation
            humans = estimator.inference(show)
            # get pose info
            pose = TfPoseVisualizer.draw_pose_rgb(show, humans)  # return frame, joints, bboxes, xcenter
            # recognize the action framewise
            show = framewise_recognize(pose, action_classifier)

            height, width = show.shape[:2]
            # 显示实时FPS值
            if (time.time() - start_time) > fps_interval:
               # 计算这个interval过程中的帧数，若interval为1秒，则为FPS
               realtime_fps = fps_count / (time.time() - start_time)
               fps_count = 0  # 帧数清零
               start_time = time.time()
            fps_label = 'FPS:{0:.2f}'.format(realtime_fps)
            cv.putText(show, fps_label, (width-160, 25), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            # 显示检测到的人数
            num_label = "Human: {0}".format(len(humans))
            cv.putText(show, num_label, (5, height-45), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            # 显示目前的运行时长及总帧数
            if frame_count == 1:
                run_timer = time.time()
            run_time = time.time() - run_timer
            time_frame_label = '[Time:{0:.2f} | Frame:{1}]'.format(run_time, frame_count)
            cv.putText(show, time_frame_label, (5, height-15), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            cv.imshow('Action Recognition based on OpenPose', show)
            video_writer.write(show)


            # 采集数据，用于训练过程(for training)
            # joints_norm_per_frame = np.append(pose[-1], args.type).astype(np.str)
            scene_joints_per_frame = np.append(pose[-1], get_action_code(args.type)).astype(np.str)
            if len(scene_joints_per_frame):
                # print('当前采集的数据是:\n')
                # print(joints_norm_per_frame)
                writer.writerow(scene_joints_per_frame)
            else:
                print('当前没有采集到数据:-<')

    video_writer.release()
    cap.release()
    f.close()

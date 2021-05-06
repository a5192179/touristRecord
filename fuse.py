import os
import numpy as np
import json

import flask
# from flask import render_template
# from flask import Response
# from flask import Flask, jsonify

import threading
import requests
import argparse

import moviepy.editor as mp
from moviepy.editor import afx
import os
from natsort import natsorted

app = flask.Flask(__name__)
thread_fuses = []

def stitchVideos(multi_video_list, result_path, tourist_id, time, music_path):
    '''
    tourist_id: str
    age: int
    gender: str
    time: YYYY-MM-DD-HH-MM-SS
    weather_id:str
    season_id:str
    result file:id_timestamp_age_gender.mp4
    audio file: base_path/age_gender_weather_season.mp3
    '''
    L = []
    for videoFile in multi_video_list:
        video = mp.VideoFileClip(videoFile)
        L.append(video)
    # L = multi_video_list
    # 拼接视频
    final_clip_video = mp.concatenate_videoclips(L)
    print(final_clip_video.duration)

    #获取音频
    audioFile = music_path
    audioclip = mp.AudioFileClip(audioFile)
    #audioclip = audioclip.subclip(0, 30)
    print('audioclip.duration:', audioclip.duration)

    #判断视频文件和音频文件的长度，从而做出不同处理
    if final_clip_video.duration < audioclip.duration:
        new_audioclip = audioclip.subclip(0, final_clip_video.duration)
        f = final_clip_video.set_audio(new_audioclip)
    else:
        #当音频时长小于视频时长，对音频做循环播放处理
        new_audioclip = audioclip.fx(afx.audio_loop, duration = final_clip_video.duration)
        f = final_clip_video.set_audio(new_audioclip)

    #result_path如果不存在，则创建
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    #生成目标视频文件
    fileName = result_path + '/' + tourist_id + '_' + time + '.mp4'
    final_clip_video_audio = f.write_videofile(fileName, fps=24, remove_temp=False)
    # exit_target = result_path + "/target.mp4"
    # if not os.path.exists(exit_target):
    #     print("move mp4 file to result path")
    #     #将拼接好的视频拷贝到result_path
    #     shutil.move(fileName, result_path)
    print("video and audio done ")

class Tourist:
    def __init__(self, scenic_area_name='', id = -1, timestamp = -1, locs = [], paths = [], fuse_path = [], music_path = '', result_path = ''):
        self.scenic_area_name = scenic_area_name
        self.id = id
        self.timestamp = timestamp
        self.locs = locs
        self.paths = paths
        self.fuse_path = fuse_path
        self.music_path = music_path
        self.result_path = result_path
        self.bFused = False
        self.bReturn = False

    def send_json(self):
        path = self.result_path + '/' + self.id + '_' + self.timestamp + '.mp4'
        scenicId = self.scenic_area_name
        touristId = self.id
        json_data = {'scenicId':scenicId, 'touristId':touristId, 'path':os.path.abspath(path)}
        r = requests.post("http://127.0.0.1:8084/algo/v1/video/saveVideo", json=json_data)
    
    def fuse(self):
        stitchVideos(self.fuse_path, self.result_path, self.id, self.timestamp, self.music_path)
        self.bFused = True
        self.send_json()
        self.bReturn = True

def fuse_all_tourist(tourist_infos):
    print('video fuse start')
    for tourist_info in tourist_infos:
        tourist_info.fuse()
    print('video fuse over')
        
@app.route('/algo/v1/video/fuse/status', methods=['GET', 'POST'])
def getStatus():
    bAlive = False
    print('len(thread_fuses)', len(thread_fuses))
    for thread in thread_fuses:
        if thread.is_alive():
            bAlive = True
            break
    if bAlive:
        return flask.jsonify({'code':0, 'status': 1, 'msg': 'face fusion is running'})
    else:
        return flask.jsonify({'code':0, 'status': 0, 'msg': 'face fusion is over'})
    

@app.route('/algo/v1/video/fuse', methods=['GET', 'POST'])
def testFlask():
    try:
        print('get')
        data = json.loads(flask.request.get_data(as_text=True))
        scenic_area_name = data['scenic_area_name']
        print('scenic_area_name:', scenic_area_name)
        # 1.get base videos
        music_path = data['base_path']['music_path']
        result_path = data['result_path']
        locs_base = []
        video_base = []
        orders = []
        for video_path in data['base_path']['video_path']:
            orders.append(video_path['order'])
            locs_base.append('')
            video_base.append('')
        base_num = len(orders)
        for i in range(base_num):
            order = orders[i]
            locs_base[int(order)] = data['base_path']['video_path'][i]['location_id']
            video_base[int(order)] = data['base_path']['video_path'][i]['path']
        # 2.fuse each tourist
        tourist_num = len(data['tourist'])
        print('base_num:', base_num, 'tourist_num:', tourist_num)
        tourist_infos = []
        for i in range(tourist_num):
            tourist_id = data['tourist'][i]['tourist_id']
            loc_num = len(data['tourist'][i]['clipped_path'])
            locs = []
            paths = []
            timestamps = []
            for j in range(loc_num):
                locs.append(data['tourist'][i]['clipped_path'][j]['location_id'])
                paths.append(data['tourist'][i]['clipped_path'][j]['path'])
                timestamps.append(data['tourist'][i]['clipped_path'][j]['timestamp'])
            fuse_path = []
            for j in range(base_num):
                fuse_path.append(video_base[j])
                for k in range(loc_num):
                    if locs[k] == locs_base[j]:
                        fuse_path.append(paths[k])
                        break
            tourist_infos.append(Tourist(scenic_area_name, tourist_id, timestamps[0], locs, paths, fuse_path, music_path, result_path))
        thread_fuse = threading.Thread(target=fuse_all_tourist, args=(tourist_infos,))
        thread_fuses.append(thread_fuse)
        thread_fuse.start()
        return flask.jsonify({'code': 0, 'error_msg': 'successful receipt'})
    except Exception as e:
        return flask.jsonify({'code': 1, 'error_msg': 'wrong input'})

def add_args(ap):
    ap.add_argument("-i", "--ip", type=str, required=True,
        help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
        help="ephemeral port number of the server (1024 to 65535)")
    # ap.add_argument("-f", "--frame-count", type=int, default=5,
    #     help="# of frames used to construct the background model")
    # ap.add_argument("-t", "--tp_points_choose", type=list, default=[(794, 460), (642, 410), (646, 192), (737, 130), (790, 172)],
    #     help="# of frames used to choose the dangerous area")
    # ap.add_argument("-c", "--configPath", type=str, default='model/person_yolov4.cfg',
    #     help="# config file of model")
    # ap.add_argument("-w", "--weightPath", type=str, default='model/person_yolov4.weights',
    #     help="# weight file of model")
    # ap.add_argument("-n", "--namePath", type=str, default="model/person.names",
    #     help="# label of model")
    return ap

if __name__ == '__main__':

    app.run(host='127.0.0.1', port=9000, debug=True,
        threaded=True, use_reloader=False)
    
    # ap = argparse.ArgumentParser()
    # ap = add_args(ap)
    # args = vars(ap.parse_args())
    # # start the flask app
    # app.run(host=args["ip"], port=args["port"], debug=True,
    #     threaded=True, use_reloader=False)
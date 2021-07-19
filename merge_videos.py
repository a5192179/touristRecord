# !/usr/bin/python
#from moviepy.editor import *
import moviepy.editor as mp
from moviepy.editor import afx
import os
from natsort import natsorted
import shutil

def merge_videos(multi_video_list, result_path):

    # 定义一个数组
    L = []

    # 访问 video 文件夹 (假设视频都放在这里面)
    for root, dirs, files in os.walk(multi_video_list):
        # 按文件名排序
        #files.sort()
        files = natsorted(files)
        # 遍历所有文件
        for file in files:
            # 如果后缀名为 .mp4
            if os.path.splitext(file)[1] == '.mp4':
                # 拼接成完整路径
                filePath = os.path.join(root, file)
                # 载入视频
                video = mp.VideoFileClip(filePath)
                # 添加到数组
                L.append(video)

    # 拼接视频
    final_clip_video = mp.concatenate_videoclips(L)
    print(final_clip_video.duration)

    #获取音频
    audioclip = mp.AudioFileClip("../data/base_videos/30_male_0_0.mp3")
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
    final_clip_video_audio = f.write_videofile("./target.mp4", fps=24, remove_temp=False)
    exit_target = result_path + "/target.mp4"
    if not os.path.exists(exit_target):
        print("move mp4 file to result path")
        #将拼接好的视频拷贝到result_path
        shutil.move("./target.mp4", result_path)
    print("video adn audio done ")

if __name__ == '__main__':
    videoFolder = '../data/tennis/test/test'
    merge_videos(videoFolder, videoFolder)



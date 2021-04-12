import os
import numpy as np
import json

import moviepy.editor as mp
from moviepy.editor import afx
import os
from natsort import natsorted

def getTouristVideo(tourist_id, clipped_path):
    '''
    tourist_id: str
    age: int
    gender: str
    time: YYYY-MM-DD-HH-MM-SS
    weather_id:str
    season_id:str
    '''
    filesName = os.listdir(clipped_path)
    touristVideos = []
    touristLocations = []
    age = -1
    for fileName in filesName:
        temp = fileName.split('.')
        if temp[-1] != 'mp4':
            continue
        temp = temp[0].split('_')
        if len(temp) > 1 and temp[0] == tourist_id:
            videoPath = clipped_path + '/' + fileName
            touristVideos.append(videoPath)
            touristLocations.append(temp[1])
            if age == -1:
                time = temp[2]
                age = int(temp[3])
                if age < 15:
                    age = 10
                elif age < 60:
                    age = 30
                else:
                    age = 60
                gender = temp[4]
                locationName = temp[1].split('-')[0]
    return touristVideos, touristLocations, age, gender, time, locationName


def getBaseVideo(locationName, weather_id, season_id, base_path, age, gender):
    '''
    locationName: str
    age: int 
    gender: 'male' 'female'
    base file: base_path/locationID_age_gender_weather_season_order.mp4
    '''
    if age < 15:
        age = 10
    elif age < 60:
        age = 30
    else:
        age = 60

    f = open(base_path + '/base.json') #可以使用 encoding='utf-8'
    content = f.read()#使用loads()方法，需要先读文件
    data = json.loads(content)
    targetName = locationName + '_' +  str(age) + '_' + gender + '_' + weather_id + '_' + season_id
    if not targetName in data:
        print(targetName, 'is not exist base video, use default')
        targetName = 'xc_30_male_0_0'
    baseVideos = data[targetName]
    baseLocations = []
    for baseName in baseVideos:
        temp = baseName.split('_')
        baseLocations.append(temp[0])
    for i in range(len(baseVideos)):
        baseVideos[i] = base_path + '/' + baseVideos[i] + '.mp4'
    return baseVideos, baseLocations
    # filesName = os.listdir(base_path)
    # fileNum = len(filesName)
    # info = np.zeros([fileNum, 4], dtype=np.int8) #index location order
    # baseVideos = []
    # baseLocations = []
    # tempBaseVideos = []
    # tempBaseLocations = []
    # baseNum = 0
    # for fileName in filesName:
    #     temp = fileName.split('.')
    #     if temp[-1] != 'mp4':
    #         continue
    #     temp = temp[0].split('_')
    #     baseAge = int(int(temp[1]) / 10) * 10
    #     if age == baseAge and gender == temp[2] and weather == int(temp[3]) and season == int(temp[4]):
    #         tempBaseVideos.append(base_path + '/' + fileName)
    #         tempBaseLocations.append(int(temp[0]))
    #         info[baseNum, 0] = baseNum
    #         info[baseNum, 1] = tempBaseLocations[baseNum]
    #         info[baseNum, 2] = int(temp[5])
    #         baseNum += 1
    # info = info[0:baseNum, :]
    # info = info[np.argsort(info[:, 1]), :]
    # oriIndex = []
    # while i < baseNum - 1:
    #     if info[i, 1] == info[i + 1, 1]:
    #         oriIndex.append(i)
    #         i += 1
    #     elif len(oriIndex) > 0:
    #         beginRow = oriIndex[0]
    #         endRow = oriIndex[-1]
    #         temp = info[beginRow:endRow, :]
    #         temp = temp[np.argsort(temp[:, 2]), :]
    #         info[beginRow:endRow, :] = temp
    #         oriIndex = []
    #         i += 1
    #     else:
    #         i += 1
    # while i < baseNum:
    #     baseVideos.append(tempBaseVideos[info[i, 0]])
    #     baseLocations.append(tempBaseLocations[info[i, 0]])
    # return baseVideos, baseLocations

def stitchVideos(multi_video_list, result_path, tourist_id, age, gender, time, base_path, weather_id, season_id):
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
    # # 定义一个数组
    # L = []

    # # 访问 video 文件夹 (假设视频都放在这里面)
    # for root, dirs, files in os.walk(multi_video_list):
    #     # 按文件名排序
    #     #files.sort()
    #     files = natsorted(files)
    #     # 遍历所有文件
    #     for file in files:
    #         # 如果后缀名为 .mp4
    #         if os.path.splitext(file)[1] == '.mp4':
    #             # 拼接成完整路径
    #             filePath = os.path.join(root, file)
    #             # 载入视频
    #             video = mp.VideoFileClip(filePath)
    #             # 添加到数组
    #             L.append(video)
    L = []
    for videoFile in multi_video_list:
        video = mp.VideoFileClip(videoFile)
        L.append(video)
    # L = multi_video_list
    # 拼接视频
    final_clip_video = mp.concatenate_videoclips(L)
    print(final_clip_video.duration)

    #获取音频
    audioFile = base_path + '/' + str(age) + '_' + gender + '_' + weather_id + '_' + season_id + '.mp3'
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
    fileName = result_path + '/' + str(tourist_id) + '_' + time + '_' + str(age) + '_' + gender + '.mp4'
    final_clip_video_audio = f.write_videofile(fileName, fps=24, remove_temp=False)
    # exit_target = result_path + "/target.mp4"
    # if not os.path.exists(exit_target):
    #     print("move mp4 file to result path")
    #     #将拼接好的视频拷贝到result_path
    #     shutil.move(fileName, result_path)
    print("video and audio done ")

def fuseVideos(tourist_id, weather_id, season_id, clipped_path, base_path, result_path):
    '''
    tourist file:id_locationID_timestamp_age_gender.mp4 ls-1-1616515915847-30-male.mp4
    result file:id_timestamp_age_gender.mp4
    audio file: base_path/age_gender_weather_season.mp3
    base file: base_path/locationID_age_gender_weather_season_order.mp4
    '''
    touristVideos, touristLocations, age, gender, time, locationName = getTouristVideo(tourist_id, clipped_path)
    baseVideos, baseLocations = getBaseVideo(locationName, weather_id, season_id, base_path, age, gender)
    baseNum = 0
    videoList = []
    for baseVideo in baseVideos:
        location = baseLocations[baseNum]
        if baseNum + 1 < len(baseVideos) and baseLocations[baseNum + 1] == location:
            # no tourist video
            videoList.append(baseVideo)
            baseNum += 1
            continue
        for i in range(len(touristLocations)):
            if touristLocations[i] == location:
                videoList.append(baseVideo)
                videoList.append(touristVideos[i])
                break
        baseNum += 1
    stitchVideos(videoList, result_path, tourist_id, age, gender, time, base_path, weather_id, season_id)
    return True

if __name__ == '__main__':
    tourist_id = 'zyl'
    weather_id = '0'
    season_id = '0'
    clipped_path = '../data/clipped_videos'
    base_path = '../data/base_videos'
    result_path = '../data/result_videos'
    # age = 33
    # gender = 'male'
    # locationName = 'xc'
    fuseVideos(tourist_id, weather_id, season_id, clipped_path, base_path, result_path)
    # getBaseVideo(locationName, weather_id, season_id, base_path, age, gender)


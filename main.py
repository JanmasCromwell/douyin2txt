# -*- coding: utf-8 -*-
import array
import multiprocessing
import os.path
import queue
import uuid
import requests
from ffmpeg import FFmpeg
import speech_recognition as sr
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def initWeb(pageUrl):
    option = Options()
    option.add_argument("--headless")  # 给option对象添加无头参数
    excetureService = Service(r"E:\Python\Tools\chromedriver\113.0.5672.63.exe")
    web = Chrome(service=excetureService)
    web.maximize_window()  # 窗口最大化
    web.get(pageUrl)
    return web


def downVideo(web, title=''):
    if len(title) == 0:
        title = uuid.uuid4()

    # /html/body/div[2]/div[1]/div[2]/div[2]/div/div[1]/div[2]/div/xg-video-container/video/source[2]
    source = web.find_element(By.XPATH,
                              '/html/body/div[2]/div[1]/div[2]/div[2]/div/div[1]/div[2]/div/xg-video-container/video/source[2]')
    videoSrc = source.get_attribute('src')

    filepath = 'video/' + str(title) + '.mp4'
    print('正在下载视频 %s' % title)
    r = requests.get(videoSrc)
    if not os.path.isdir('video'):
        os.mkdir('video')

    with open(filepath, 'wb') as fp:
        fp.write(r.content)
    print('%s已下载' % title)
    return filepath


def toMp3(filePath, title=''):
    if len(title) == 0:
        title = uuid.uuid4()
    mp3Path = 'mp3/' + str(title) + '.mp3'
    if not os.path.isdir('mp3'):
        os.mkdir('mp3')

    if not os.path.isfile(filePath) or os.path.getsize(filePath) <= 0:
        print('视频文件%s不存在' % title)
        os.system('pause')
    if not os.path.isfile(mp3Path):
        file = open(mp3Path, 'w')
        file.close()
    ffmpeg = (
        FFmpeg().option('y').input(url=filePath).output(url=mp3Path)
    )
    ffmpeg.execute()
    return mp3Path


def toWav(mp3Path, title):
    if not os.path.isfile(mp3Path) or os.path.getsize(mp3Path) <= 0:
        print('mp3文件%s不存在' % title)
        os.system('pause')

    wavPath = 'wav/' + str(title) + '.wav'
    if not os.path.isdir('wav'):
        os.mkdir('wav')
    if not os.path.isfile(wavPath):
        file = open(wavPath, 'w')
        file.close()
    ffmpeg = (
        FFmpeg().option('y').input(url=mp3Path).output(url=wavPath)
    )

    ffmpeg.execute()
    return wavPath


def exportTxt(wavPath, title):
    if len(title) == 0:
        title = uuid.uuid4()
    txtFile = 'txt/' + title + '.txt'
    if not os.path.isdir('txt'):
        os.mkdir('txt')

    if not os.path.isfile(wavPath) or os.path.getsize(wavPath) <= 0:
        print('音频文件%s不存在' % title)
        os.system('pause')

    r = sr.Recognizer()
    with sr.AudioFile(wavPath) as src:
        audio = r.record(src)

    text = r.recognize_sphinx(audio, language="zh-CN")

    txtFileSteam = open(txtFile, 'w', encoding='utf-8')
    txtFileSteam.write(text)
    txtFileSteam.close()
    print("%s识别完成" % title)


def delFiles(filesArray):
    for f in filesArray:
        os.remove(f)


def handleQueue(queue):
    while True:
        pageUrl = queue.get()
        web = initWeb(pageUrl)
        title = web.title
        videoPath = downVideo(web, title)
        print("转录为mp3格式......")
        mp3Path = toMp3(videoPath, title)
        print("转录为wav格式......")
        wavPath = toWav(mp3Path, title)
        print("文件识别开始.......")
        exportTxt(wavPath, title)
        filesArray = [videoPath, mp3Path, wavPath]
        delFiles(filesArray)


# option.
if __name__ == "__main__":
    queue = multiprocessing.Queue(3)
    pro = multiprocessing.Process(target=handleQueue, args=(queue,))
    pro.start()
    l = open('links.txt', 'r', encoding='utf-8')
    while True:
        links = l.readline()
        if not links:
            break
        print(links)
        queue.put(links)
        print(queue.qsize())

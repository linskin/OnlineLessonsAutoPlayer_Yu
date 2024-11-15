'''
Author: LetMeFly
Date: 2023-09-12 20:49:21
LastEditors: LetMeFly
LastEditTime: 2023-12-22 23:32:59
Description: 开源于https://github.com/LetMeFly666/YuketangAutoPlayer 欢迎issue、PR
'''
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import random

IF_HEADLESS = False  # 是否以无窗口模式运行（首次运行建议使用有窗口模式以观察是否符合预期）
COURSE_URL = 'https://nwnu.yuketang.cn/pro/lms/9mmGBp8hbja/16444474/studycontent'  # 要刷的课的地址（获取方式见README）
COOKIE = '7jy2ekqwzyuaie0c85ya98pb1g54jhu6'  # 打死也不要告诉别人哦（获取方式见README）

option = webdriver.ChromeOptions()

if IF_HEADLESS:
    option.add_argument('--headless')

driver = webdriver.Chrome(options=option)
driver.maximize_window()
IMPLICITLY_WAIT = 10
driver.implicitly_wait(IMPLICITLY_WAIT)
IS_COMMOONUI = False


def str2dic(s):
    d = dict()
    for i in s.split('; '):
        temp = i.split('=')
        d[temp[0]] = temp[1]
    return d


def setCookie(cookies):
    driver.delete_all_cookies()
    for name, value in cookies.items():
        driver.add_cookie({'name': name, 'value': value, 'path': '/'})


def ifVideo(div):
    global tempDiv
    for i in div.find_elements(By.TAG_NAME, 'i'):
        i_class = i.get_attribute('class')
        if 'icon--suo' in i_class:  # 锁的图标，表明视频未开放
            return False
    try:
        i = div.find_element(By.TAG_NAME, 'i')
    except:
        return False  # 每个小结后面都存在空行<li>
    i_class = i.get_attribute('class')
    return 'icon--shipin' in i_class


def getAllvideos_notFinished(allClasses):
    driver.implicitly_wait(0.1)  # 找不到元素时会找满implicitly_wait秒
    allVideos = []
    for thisClass in allClasses:
        if ifVideo(thisClass) and '已完成' not in thisClass.text:
            allVideos.append(thisClass)
    driver.implicitly_wait(IMPLICITLY_WAIT)
    return allVideos


def get1video_notFinished(allClasses):
    for thisClass in allClasses:
        if ifVideo(thisClass) and '已完成' not in thisClass.text:
            return thisClass
    return None




def change2speed2():
    speedbutton = driver.find_element(By.TAG_NAME, 'xt-speedbutton')
    ActionChains(driver).move_to_element(speedbutton).perform()
    ul = speedbutton.find_element(By.TAG_NAME, 'ul')
    lis = ul.find_elements(By.TAG_NAME, 'li')
    li_speed2 = lis[0]
    diffY = speedbutton.location['y'] - li_speed2.location['y']
    # ActionChains(driver).move_to_element_with_offset(speedbutton, 3, 5).perform()
    # ActionChains(driver).click().perform()
    # 我也不知道为啥要一点一点移动上去，反正直接移动上去的话，点击是无效的
    for i in range(diffY // 10):  # 可能不是一个好算法
        ActionChains(driver).move_by_offset(0, -10).perform()
        sleep(0.5)
    sleep(0.8)
    ActionChains(driver).click().perform()


def mute1video():
    if driver.execute_script('return video.muted;'):
        return
    voice = driver.find_element(By.TAG_NAME, 'xt-volumebutton')
    ActionChains(driver).move_to_element(voice).perform()
    ActionChains(driver).click().perform()


def finish1video():
    if IS_COMMOONUI:
        scoreList = driver.find_element(By.ID, 'tab-student_school_report')
        scoreList.click()
        allClasses = driver.find_elements(By.CLASS_NAME, 'study-unit')
    else:
        allClasses = driver.find_elements(By.CLASS_NAME, 'leaf-detail')
    print('正在寻找未完成的视频，请耐心等待')
    allVideos = getAllvideos_notFinished(allClasses)
    if not allVideos:
        return False
    video = allVideos[0]
    driver.execute_script('arguments[0].scrollIntoView(false);', video)
    if IS_COMMOONUI:
        span = video.find_element(By.TAG_NAME, 'span')
        span.click()
    else:
        video.click()
    print('正在播放')
    driver.switch_to.window(driver.window_handles[-1])
    WebDriverWait(driver, 10).until(lambda x: driver.execute_script(
        'video = document.querySelector("video"); console.log(video); return video;'))  # 这里即使2次sleep3s选中的video还是null
    driver.execute_script('videoPlay = setInterval(function() {if (video.paused) {video.play();}}, 200);')
    driver.execute_script('setTimeout(() => clearInterval(videoPlay), 5000)')
    driver.execute_script(
        'addFinishMark = function() {finished = document.createElement("span"); '
        'finished.setAttribute("id", "LetMeFly_Finished"); '
        'document.body.appendChild(finished); console.log("Finished");}')
    driver.execute_script(
        'lastDuration = 0; setInterval(() => {nowDuration = video.currentTime; '
        'if (nowDuration < lastDuration) {addFinishMark()}; '
        'lastDuration = nowDuration}, 200)')
    driver.execute_script('video.addEventListener("pause", () => {video.play()})')
    mute1video()
    change2speed2()
    while True:
        if driver.execute_script('return document.querySelector("#LetMeFly_Finished");'):
            print('finished, wait 5s')
            sleep(5)  # 再让它播5秒
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
            return True
        else:
            print(f'正在播放视频 | not finished yet | 随机数: {random.random()}')
            sleep(3)
    return False



COURSE_URL_LIST = ["https://nwnu.yuketang.cn/pro/lms/Adri46cNpNJ/16444433/studycontent",
    "https://nwnu.yuketang.cn/pro/lms/9mmGBp8hbja/16444474/studycontent"
    , "https://nwnu.yuketang.cn/pro/lms/9mmGBp8jBbc/16444472/studycontent"
    , "https://nwnu.yuketang.cn/pro/lms/9mmGBp92fEk/16444475/studycontent"
    , "https://nwnu.yuketang.cn/pro/lms/ACuTgbmSA6c/16444488/studycontent"
    , "https://nwnu.yuketang.cn/pro/lms/9mmGBp8xU5W/16444473/studycontent"
    , "https://nwnu.yuketang.cn/pro/lms/Adri46cNpNJ/16444433/studycontent"]

for URL in COURSE_URL_LIST:
    COURSE_URL = URL
    driver = webdriver.Chrome(options=option)
    driver.maximize_window()
    IMPLICITLY_WAIT = 10
    driver.implicitly_wait(IMPLICITLY_WAIT)
    # IS_COMMOONUI = False
    homePageURL = 'https://' + COURSE_URL.split('https://')[1].split('/')[0] + '/'
    if 'www.yuketang.cn' in homePageURL:
        IS_COMMOONUI = True
    # driver.get('https://grsbupt.yuketang.cn/')
    driver.get(homePageURL)
    setCookie({'sessionid': COOKIE})
    driver.get(COURSE_URL)
    sleep(3)
    if 'pro/portal/home' in driver.current_url:
        print('cookie失效或设置有误，请重设cookie或选择每次扫码登录')
        driver.get(homePageURL)
        driver.find_element(By.CLASS_NAME, 'login-btn').click()
        print("请扫码登录")
        while 'courselist' not in driver.current_url:  # 判断是否已经登录成功
            sleep(0.5)
        print('登录成功')
        driver.get(COURSE_URL)
    while finish1video():
        driver.refresh()
    driver.quit()
    print('恭喜你！全部播放完毕')
    sleep(5)

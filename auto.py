import concurrent.futures

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import random
import threading


class VideoPlayer:
    def __init__(self, headless=False):
        self.option = webdriver.ChromeOptions()
        if headless:
            self.option.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.option)
        self.driver.maximize_window()
        self.IMPLICITLY_WAIT = 10
        self.IS_COMMOONUI = False
        self.semaphore = threading.Semaphore(1)  # Set the maximum number of threads

    def set_cookie(self, cookies):
        self.driver.delete_all_cookies()
        for name, value in cookies.items():
            self.driver.add_cookie({'name': name, 'value': value, 'path': '/'})

    def if_video(self, div):
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

    def get_all_videos_not_finished(self, all_classes):
        self.driver.implicitly_wait(0.1)  # 找不到元素时会找满implicitly_wait秒
        all_videos = []
        for this_class in all_classes:
            if self.if_video(this_class) and '已完成' not in this_class.text:
                all_videos.append(this_class)
        self.driver.implicitly_wait(self.IMPLICITLY_WAIT)
        return all_videos

    def change_to_speed2(self):
        speedbutton = self.driver.find_element(By.TAG_NAME, 'xt-speedbutton')
        ActionChains(self.driver).move_to_element(speedbutton).perform()
        ul = speedbutton.find_element(By.TAG_NAME, 'ul')
        lis = ul.find_elements(By.TAG_NAME, 'li')
        li_speed2 = lis[0]
        diffY = speedbutton.location['y'] - li_speed2.location['y']
        for i in range(diffY // 10):
            ActionChains(self.driver).move_by_offset(0, -10).perform()
            sleep(0.5)
        sleep(0.8)
        ActionChains(self.driver).click().perform()

    def mute_video(self):
        if self.driver.execute_script('return video.muted;'):
            return
        # mute_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Mute']")
        # mute_button.click()
        voice = self.driver.find_element(By.TAG_NAME, 'xt-volumebutton')
        ActionChains(self.driver).move_to_element(voice).perform()
        ActionChains(self.driver).click().perform()

    def finish_video(self):
        all_classes = self.driver.find_elements(By.CLASS_NAME, 'leaf-detail')
        print('正在寻找未完成的视频，请耐心等待')
        all_videos = self.get_all_videos_not_finished(all_classes)
        if not all_videos:
            return False
        video = all_videos[0]
        self.driver.execute_script('arguments[0].scrollIntoView(false);', video)
        video.click()
        print('正在播放')
        self.driver.switch_to.window(self.driver.window_handles[-1])
        WebDriverWait(self.driver, 10).until(lambda x: self.driver.execute_script(
            'video = document.querySelector("video"); return video;'))
        self.driver.execute_script('videoPlay = setInterval(function() {if (video.paused) {video.play();}}, 200);')
        self.driver.execute_script('setTimeout(() => clearInterval(videoPlay), 5000)')
        self.driver.execute_script(
            'addFinishMark = function() {finished = document.createElement("span"); '
            'finished.setAttribute("id", "LetMeFly_Finished"); '
            'document.body.appendChild(finished); console.log("Finished");}')
        self.driver.execute_script(
            'lastDuration = 0; setInterval(() => {nowDuration = video.currentTime; '
            'if (nowDuration < lastDuration) {addFinishMark()}; '
            'lastDuration = nowDuration}, 200)')
        self.driver.execute_script('video.addEventListener("pause", () => {video.play()})')
        self.mute_video()
        self.change_to_speed2()
        while True:
            if self.driver.execute_script('return document.querySelector("#LetMeFly_Finished");'):
                print('finished, wait 5s')
                sleep(5)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[-1])
                return True
            else:
                print(f'正在播放视频 | not finished yet | 随机数: {random.random()}')
                sleep(3)
        return False

    def play_course(self, course_url, cookie):
        self.semaphore.acquire()  # Acquire a semaphore before starting the thread
        self.driver.get(course_url)
        sleep(3)
        home_page_url = 'https://' + course_url.split('https://')[1].split('/')[0] + '/'
        if 'www.yuketang.cn' in home_page_url:
            self.IS_COMMOONUI = True
        self.set_cookie({'sessionid': cookie})
        self.driver.get(course_url)
        sleep(3)
        if 'pro/portal/home' in self.driver.current_url:
            print('cookie失效或设置有误，请重设cookie或选择每次扫码登录')
            self.driver.get(home_page_url)
            self.driver.find_element(By.CLASS_NAME, 'login-btn').click()
            print("请扫码登录")
            while 'courselist' not in self.driver.current_url:
                sleep(0.5)
            print('登录成功')
            self.driver.get(course_url)
        while self.finish_video():
            self.driver.refresh()
        self.driver.quit()
        print('恭喜你！全部播放完毕')
        sleep(5)
        self.semaphore.release()  # Release the semaphore when the thread completes


def play_in_thread(course_url, cookie, headless):
    player = VideoPlayer(headless=headless)
    player.play_course(course_url, cookie)


def manage_threads(course_url_list, cookie, headless, max_workers=3):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务到线程池
        futures = []
        for url in course_url_list:
            future = executor.submit(play_in_thread, url, cookie, headless)
            futures.append(future)

        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"发生了一个错误，错误信息为: {e}")


if __name__ == "__main__":
    COURSE_URL_LIST = [
        "https://nwnu.yuketang.cn/pro/lms/9mmGBp8hbja/16444474/studycontent",
        "https://nwnu.yuketang.cn/pro/lms/9mmGBp8jBbc/16444472/studycontent",
        "https://nwnu.yuketang.cn/pro/lms/9mmGBp92fEk/16444475/studycontent",
        "https://nwnu.yuketang.cn/pro/lms/ACuTgbmSA6c/16444488/studycontent",
        "https://nwnu.yuketang.cn/pro/lms/9mmGBp8xU5W/16444473/studycontent",
        "https://nwnu.yuketang.cn/pro/lms/Adri46cNpNJ/16444433/studycontent"
    ]
    COOKIE = 'n17vt928119qxhl94fdegoydn45x8osd'
    max_workers = 3
    headless = True
    manage_threads(COURSE_URL_LIST, COOKIE,headless, max_workers)

import os
import sys
from time import sleep

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from faculty import faculty_dict


def get_driver():
    """driver setup"""
    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split(".")[0]
    driver_path = f"./{chrome_ver}/chromedriver"
    if os.path.exists(driver_path):
        print(f"chrome driver is installed: {driver_path}")
    else:
        print(f"install the chrome driver(ver: {chrome_ver})")
        chromedriver_autoinstaller.install(True)

    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {"download.default_directory": os.getcwd()})

    options = ["--headless", "--no-sandbox"]
    for option in options:
        chrome_options.add_argument(option)
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def login_action(hisnet_id: str, pwd: str, driver):
    """login to hisnet"""
    driver.switch_to.frame('MainFrame')

    driver.find_element(By.CSS_SELECTOR, "input[name='id_1']").send_keys(hisnet_id)

    driver.find_element(By.CSS_SELECTOR, "input[name='password_1']").send_keys(pwd)

    driver.find_element(By.CSS_SELECTOR, "input[src='/2012_images/intro/btn_login.gif']").click()
    sleep(5)


def course_info(base_url: str, year: str, term: str, faculty: str, driver):
    """get the information of course"""
    driver.get(base_url)
    sleep(3)

    Select(driver.find_element(By.NAME, 'hak_year')).select_by_visible_text(year)

    Select(driver.find_element(By.NAME, 'hak_term')).select_by_visible_text(term)

    if faculty == "%C0%FC%C3%BC":
        pass
    elif faculty == "창의융합교육원":
        driver.find_element(By.NAME, 'gwamok_code').send_keys("CCE")
    else:
        Select(driver.find_element(By.NAME, 'hakbu')).select_by_visible_text(faculty)

    driver.find_element(By.CSS_SELECTOR, "a[href='javascript:sendit()']").click()
    sleep(3)


def main(base_url: str):
    """crawler generation"""
    driver = get_driver()
    driver.get("https://hisnet.handong.edu/")
    sleep(3)

    try:
        hisnet_id = input("HISNet ID를 입력하시오: ")
        pwd = input("Password를 입력하시오: ")

        login_action(hisnet_id, pwd, driver)

        answer = input("조회를 원하는 학기와 연도를 다음 형식에 맞춰 입력하시오 (ex: 2021-2): ")
        year = answer.split("-")[0]
        term = answer.split("-")[1]
        faculty = input("조회를 원하는 학부의 이름을 입력하시오 (전체 입력시, 모든 학부의 정보 조회 가능): ")
        cce=" "

        if "전체" in faculty:
            faculty = "%C0%FC%C3%BC"
            faculty_code = "%C0%FC%C3%BC"
        elif faculty == "AI융합교육원":
            faculty = "AI융합교육원(공학)"
            faculty_code = faculty_dict[faculty]
        elif faculty == "창의융합교육원":
            cce = "CCE"
            faculty_code = "%C0%FC%C3%BC"
        else:
            faculty_code = faculty_dict[faculty]
        course_info(base_url, year, term, faculty, driver)

    except:
        driver.quit()
        print("중간에 문제가 발생하였습니다.")
        sys.exit("ERROR OCCUR")

    try:
        course_list = []
        page_num = 1
        while True:
            for cont in range(2, 17):
                course_id_path = f"table[id='att_list'] > tbody > tr:nth-child({cont}) > td:nth-child(2)"
                course_name_path = f"table[id='att_list'] > tbody > tr:nth-child({cont}) > td:nth-child(4)"
                prof_path = f"table[id='att_list'] > tbody > tr:nth-child({cont}) > td:nth-child(6)"
                syllabus_path = f"table[id='att_list'] > tbody > tr:nth-child({cont}) > td:nth-child(17)"

                course_id = driver.find_element(By.CSS_SELECTOR, course_id_path).text
                course_name = driver.find_element(By.CSS_SELECTOR, course_name_path).text
                professor_name = driver.find_element(By.CSS_SELECTOR, prof_path).text
                syllabus_status = driver.find_element(By.CSS_SELECTOR, syllabus_path).text

                if "조회" in syllabus_status:
                    course_list.append([course_id, course_name, professor_name])

            page_num+=1
            page_url = f"https://hisnet.handong.edu/for_student/course/PLES330M.php?Page={page_num}&ksearch=search&hak_year={year}&hak_term={term}&hakbu={faculty_code}&isugbn=%C0%FC%C3%BC&injung=%C0%FC%C3%BC&eng=%C0%FC%C3%BC&gwamok_code={cce}"
            driver.get(page_url)
            sleep(1)

    except Exception:
        driver.quit()
        for course in course_list:
            print(course)


if __name__ == "__main__":
    url = "https://hisnet.handong.edu/for_student/course/PLES330M.php"
    main(url)

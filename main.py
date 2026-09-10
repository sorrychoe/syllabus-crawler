import os
import platform
import re
import sys
from getpass import getpass
from time import sleep

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from faculty import faculty_dict, faculty_info


def get_driver():
    """Set up and return a configured Selenium Chrome WebDriver.

    Detects the installed Chrome major version, installs a matching
    chromedriver if one is not already present under ``./<version>/``,
    then builds a headless Chrome instance with a fixed window size,
    a download directory set to the current working directory, and a
    Naver Yeti bot user-agent string.

    Returns:
        selenium.webdriver.Chrome: The initialized WebDriver instance.
    """
    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split(".")[0]
    driver_path = f"./{chrome_ver}/chromedriver"
    if os.path.exists(driver_path):
        print(f"chrome driver is installed: {driver_path}")
    else:
        print(f"install the chrome driver(ver: {chrome_ver})")
        chromedriver_autoinstaller.install(True)

    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {"download.default_directory": os.getcwd()})

    options = ["--headless=new", "--window-size=1920,1080", "--disable-gpu"]
    for option in options:
        chrome_options.add_argument(option)

    agent = "Mozilla/5.0 (compatible; Yeti/1.1; +http://naver.me/bot)"
    chrome_options.add_argument(f"--user-agent={agent}")

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def login_action(hisnet_id: str, pwd: str, driver: any):
    """Log in to the HISNet student portal.

    Switches into the ``MainFrame`` iframe, fills the id and password
    fields, submits the login form, and then navigates to the student
    main page, waiting until the URL confirms the page has loaded.

    Args:
        hisnet_id: HISNet account id.
        pwd: HISNet account password.
        driver: Active Selenium WebDriver positioned on the HISNet
            home page.

    Raises:
        Exception: Re-raised if any step of the login flow fails
            (e.g. a form field is missing or the redirect times out).
    """
    try:
        driver.switch_to.frame('MainFrame')

        id_field = driver.find_element(By.XPATH, '//*[@id="loginBoxBg"]/table[2]/tbody/tr/td[5]/form/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/span/input')
        id_field.click()
        id_field.clear()
        id_field.send_keys(hisnet_id)

        pwd_field = driver.find_element(By.XPATH, '//*[@id="loginBoxBg"]/table[2]/tbody/tr/td[5]/form/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/input')
        pwd_field.click()
        pwd_field.clear()
        pwd_field.send_keys(pwd)

        driver.find_element(By.CSS_SELECTOR, "input[src='/2012_images/intro/btn_login.gif']").click()
        sleep(3)

        driver.get("https://hisnet.handong.edu/for_student/main.php")

        WebDriverWait(driver, 10).until(EC.url_contains('main.php'))
        print("✅ 로그인 성공!")
    except Exception as e:
        print("❌ 로그인 실패!")
        raise e


def course_info(base_url: str, year: str, term: str, faculty: str, driver: any):
    """Run the course search form for the given year, term, and faculty.

    Opens the course listing page, selects the academic year and term,
    narrows the search by faculty, and submits the form. The whole
    catalog is searched when ``faculty`` is the URL-encoded value for
    "전체"; the "창의융합교육원" case filters by the ``CCE`` subject-code
    prefix instead of the faculty dropdown.

    Args:
        base_url: URL of the course listing page (PLES330M.php).
        year: Academic year as shown in the dropdown (e.g. "2021").
        term: Academic term as shown in the dropdown (e.g. "2").
        faculty: Faculty name matching the dropdown text, the
            URL-encoded "전체" sentinel, or "창의융합교육원".
        driver: Active, logged-in Selenium WebDriver.
    """
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


def clear():
    """Clear the terminal screen.

    Runs ``cls`` on Windows and ``clear`` elsewhere, then pauses
    briefly so rapid successive clears stay readable.
    """
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')
    sleep(0.5)


def main(base_url: str):
    """Run the interactive syllabus-crawler workflow end to end.

    Prompts for HISNet credentials and logs in, asks for the target
    "year-term" and faculty, then pages through the course listing and
    collects courses whose syllabus is registered ("조회"). Prints the
    collected courses and, on request, opens one course's syllabus to
    print its overview, recognized major, and grading breakdown
    (attendance, midterm, final, quiz, team project, assignment, and
    two "기타" categories). The WebDriver is always closed before the
    function returns or exits.

    Args:
        base_url: URL of the course listing page (PLES330M.php).

    Raises:
        SystemExit: If an error occurs during login or the initial
            course search; the driver is quit first.
    """
    driver = get_driver()
    driver.get("https://hisnet.handong.edu/")
    sleep(2)

    try:
        print("         ")
        hisnet_id = input("\033[32m" + "HISNet ID를 입력하시오: " + "\033[0m")
        pwd = getpass("\033[32m" + "Password를 입력하시오: " + "\033[0m")

        login_action(hisnet_id, pwd, driver)

        answer = input("\033[32m" + "조회를 원하는 학기와 연도를 다음 형식에 맞춰 입력하시오 (ex: 2021-2): " + "\033[0m").strip()
        if not re.fullmatch(r"\d{4}-[1-4]", answer):
            raise ValueError("연도-학기 형식이 올바르지 않습니다 (ex: 2021-2)")
        year, term = answer.split("-")
        print("===============================")
        for num in faculty_info:
            print(f"{num}: {faculty_info[num]}")
        print("===============================")
        faculty_num = input("\033[32m" + "상단의 리스트를 참고하여 해당하는 학부를 선택하시오: " + "\033[0m")
        faculty = faculty_info[faculty_num]
        cce=" "

        if faculty == "전체":
            faculty = "%C0%FC%C3%BC"
            faculty_code = "%C0%FC%C3%BC"
        elif faculty == "창의융합교육원":
            cce = "CCE"
            faculty_code = "%C0%FC%C3%BC"
        else:
            faculty_code = faculty_dict[faculty]

        course_info(base_url, year, term, faculty, driver)

    except Exception as e:
        driver.quit()
        print("\033[31m" + "중간에 문제가 발생하였습니다." + "\033[0m")
        print(e)
        sys.exit("ERROR OCCUR")

    try:
        course_list = []
        page_num = 1
        i=0
        while True:
            clear()
            print("\033[31m" + "데이터 추출 중" + "."* i + "\033[0m")
            i+=1
            if i==5:
                i=1
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
        clear()
        print("\033[96m" + "현재 강의계획서가 등록된 과목 정보" + "\033[0m")
        print("=========================")
        for course in course_list:
            print(course)
        print("=========================")
        print("                         ")
        ans = input("\033[32m" + "과목의 개요 정보를 조회하시겠습니까(Y/N)?: " + "\033[0m")
        if (ans == "Y") or (ans == "y"):
            print("   ")
            course_ans = input("\033[32m" + "조회를 희망하는 강의의 과목코드를 입력하시요: " + "\033[0m").strip()
            if not re.fullmatch(r"[A-Za-z0-9]{1,20}", course_ans):
                print("\033[31m" + "과목코드는 영문/숫자만 입력 가능합니다." + "\033[0m")
                driver.quit()
                return
            page_url = f"https://hisnet.handong.edu/SMART/lp_view_4student_1.php?kang_yy={year}&kang_hakgi={term}&kang_hakgwa=0013&kang_code={course_ans}&kang_ban=01&kang_cs_code=&kang_cs_ban="
            driver.get(page_url)
            sleep(1)
            clear()

            summary = driver.find_element(By.CSS_SELECTOR, "div[id='div1'] > div > table:nth-child(13) > tbody > tr > td").text
            major = driver.find_element(By.CSS_SELECTOR, "div[id='div1'] > div > table:nth-child(2) > tbody > tr:nth-child(5) > td.cls_AlignLeft > div").text
            attendance = driver.find_element(By.CSS_SELECTOR, "div[id='div1'] > div > table:nth-child(20) > tbody> tr:nth-child(3) > td:nth-child(1)").text
            midterm = driver.find_element(By.CSS_SELECTOR, "div[id='div1'] > div > table:nth-child(20) > tbody> tr:nth-child(3) > td:nth-child(2)").text
            final = driver.find_element(By.CSS_SELECTOR, "div[id='div1'] > div > table:nth-child(20) > tbody> tr:nth-child(3) > td:nth-child(3)").text
            quiz = driver.find_element(By.CSS_SELECTOR, "div[id='div1'] > div > table:nth-child(20) > tbody> tr:nth-child(3) > td:nth-child(4)").text
            team_project = driver.find_element(By.CSS_SELECTOR, "div[id='div1'] > div > table:nth-child(20) > tbody> tr:nth-child(3) > td:nth-child(5)").text
            assignment = driver.find_element(By.CSS_SELECTOR, "div[id='div1'] > div > table:nth-child(20) > tbody> tr:nth-child(3) > td:nth-child(6)").text
            etc1 = driver.find_element(By.CSS_SELECTOR, "div[id='div1'] > div > table:nth-child(20) > tbody> tr:nth-child(3) > td:nth-child(7)").text
            etc2 = driver.find_element(By.CSS_SELECTOR, "div[id='div1'] > div > table:nth-child(20) > tbody> tr:nth-child(3) > td:nth-child(8)").text

            print("\033[31m" + "=========================" + "\033[0m")
            print("\033[36m" + "강의 개요" + "\033[0m")
            print("     ")
            print("\033[94m" + summary + "\033[0m")
            print("\033[31m" + "=========================" + "\033[0m")
            print("\033[36m" + "인정 전공"+ "\033[0m")
            print("     ")
            print("\033[94m" + major + "\033[0m")
            print("\033[31m" + "=========================" + "\033[0m")
            print("\033[36m" + "강의 평가 기준" + "\033[0m")
            print("     ")
            print("\033[95m" + "출석: " + "\033[91m" + f"{attendance}%" + "\033[0m")
            print("\033[95m" + "중간고사: " + "\033[91m" + f"{midterm}%" + "\033[0m")
            print("\033[95m" + "기말고사: " + "\033[91m" + f"{final}%" + "\033[0m")
            print("\033[95m" + "퀴즈: " + "\033[91m" + f"{quiz}%" + "\033[0m")
            print("\033[95m" + "팀프로젝트: " + "\033[91m" + f"{team_project}%" + "\033[0m")
            print("\033[95m" + "개인과제: " + "\033[91m" + f"{assignment}%" + "\033[0m")
            print("\033[95m" + "기타1: " + "\033[91m" + f"{etc1}%" + "\033[0m")
            print("\033[95m" + "기타2: " + "\033[91m" + f"{etc2}%" + "\033[0m")
            print("\033[31m" + "=========================" + "\033[0m")

            driver.quit()
        else:
            driver.quit()


if __name__ == "__main__":
    url = "https://hisnet.handong.edu/for_student/course/PLES330M.php"
    main(url)

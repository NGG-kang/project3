import io
import pathlib
import time
import os
import json
from pathlib import Path
from bs4 import BeautifulSoup
from django.core.files.images import ImageFile

from search_app.crawling.crawlselenium import selenium_setting
from search_app.models import JobPlanetInfo, CrwalingPhotos

BASE_DIR = Path(__file__).resolve().parent.parent.parent

try:
    secret_file = os.path.join(BASE_DIR, 'secrets.json')
    with open(secret_file) as f:
        secrets = json.loads(f.read())
except Exception as e:
    print("ID, PASSWORD 키가 없습니다.")
    secrets = ""


def get_secret(setting, secrets=secrets):
    """비밀 변수를 가져오거나 명시적 예외를 반환한다."""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        return ""
try:
    LOGIN_ID = get_secret("JOBPLANET_ID")
    LOGIN_PASSWORD = get_secret("JOBPLANET_PASSWORD")
except:
    LOGIN_ID = ""
    LOGIN_PASSWORD = ""


class GetJobPlanetInfo:

    def __init__(self, company_url="", enter=None, count=1):
        self.company_url = company_url
        self.enter = enter
        self.LOGIN_ID = LOGIN_ID
        self.LOGIN_PASSWORD = LOGIN_PASSWORD
        self.count = count

    SEARCH_REVIEW = "https://www.jobplanet.co.kr/reviews"
    LOGIN_URL = "https://www.jobplanet.co.kr/users/sign_in?_nav=gb"
    IS_LOGIN = False

    # TODO: 로그인 성공했는데 로그인 실패라고 뜨네(이상하게 가끔 그럼)
    def jobplanet_login(self, driver):
        driver.get(self.LOGIN_URL)
        driver.implicitly_wait(5)
        id = ""
        pw = ""
        try:
            id = driver.find_element_by_id('user_email')
            pw = driver.find_element_by_id('user_password')
        except:
            self.count+=1
            if self.count<6:
                return self.jobplanet_login(self, driver)
            else:
                print('잡플래닛 로그인부터 실패했습니다.')
                return ""

        id.click()
        id.send_keys(self.LOGIN_ID)
        time.sleep(1)
        pw.click()
        pw.send_keys(self.LOGIN_PASSWORD)
        driver.find_element_by_class_name('btn_sign_up').click()
        driver.implicitly_wait(5)
        driver.get(self.SEARCH_REVIEW)
        driver.get(self.SEARCH_REVIEW)
        driver.implicitly_wait(5)
        time.sleep(1)
        try:
            # 로그인 버튼이 있으면 실패
            driver.find_element_by_class_name('btn_txt.login')
            return False
        except:
            return True

    def get_company_url(self, company_name, driver):
        driver.implicitly_wait(5)
        if self.LOGIN_ID and self.LOGIN_PASSWORD:
            if self.jobplanet_login(driver):
                print("로그인 성공")
            else:
                print("로그인 실패, 그대로 진행합니다.")
        else:
            driver.get(self.SEARCH_REVIEW)
            driver.implicitly_wait(5)

        # DB에서 company_url이 넘어오면 기업찾기 스킵
        if self.company_url:
            print(self.company_url, "이 존재함 ㅋㅋ")
            driver.get(self.company_url)
            driver.implicitly_wait(5)
            return True

        try:
            search = driver.find_element_by_id('search_bar_search_query')
            search.send_keys(company_name)
            search.click()
            time.sleep(1)
            result = driver.find_element_by_id("search_bar_autocomplete")
        except Exception as e:
            print('검색에서 실패')
            print(e)

        # 검색 결과가 (주)를 포함한 company_name이 맞는지 확인
        try:
            result_company = result.find_elements_by_class_name("company")
            for i in result_company:
                if i.text == company_name+"(주)" or i.text == "(주)"+company_name or i.text == company_name:
                    i.click()
                    driver.implicitly_wait(10)
                    break
        except Exception as e:
            print(e)
            result_company = ""

        # 검색 결과가 없다면
        if not result_company or len(result_company) == 0:
            try:
                # 다른 부분에서 검색 결과를 찾는다.
                result_company = result.find_elements_by_class_name("row")
                for i in result_company:
                    if i.text == company_name + "(주)" or i.text == "(주)" + company_name or i.text == company_name:
                        i.click()
                        driver.implicitly_wait(10)
                        time.sleep(1)
                        break
            except Exception as e:
                print(e)
                return False
            try:
                print("검색결과 없을때 한번더 체크", driver.current_url)
                print(driver.current_url)
                driver.find_elements_by_class_name("result_card.tag_view")[0].click()
            except Exception as e:
                print(e)
            try:
                html = driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                href = soup.select_one(
                    "#mainContents > div:nth-child(1) > div > div.result_company_card > div.is_company_card > div.result_card.tag_view > a").attrs[
                    'href']
                driver.get("https://www.jobplanet.co.kr/" + href)
            except Exception as e:
                print("jobplanet에 "+company_name+"이없습니다.")
                print(e)
        return False

    def get_company_info(self, company_name):
        location = ""
        print('잡플래닛 시작')
        driver = selenium_setting()
        # 잡플래닛은 디폴트가 url을 얻지 못하고 클릭해야하므로 이동한 후 url을 수집함
        if self.get_company_url(company_name, driver):
            url = self.company_url
        else:
            url = driver.current_url
            if url == self.SEARCH_REVIEW:
                return
        company_code = url.split("/")
        jobplanet_company_name = company_code[-1]
        company_code = company_code[-3]

        path = os.path.join(BASE_DIR) + '/media/search_job/' + company_name + '/jobplanet/' + company_code + time.strftime(
            "/%Y/%m/%d/")

        REVIEW_URL = "https://www.jobplanet.co.kr/companies/" + company_code + "/reviews/"
        driver.get(REVIEW_URL)
        driver.implicitly_wait(10)
        try:
            driver.find_elements_by_class_name('btn_close_x_ty1')[0].click()
        except:
            pass
        # driver.find_element_by_class_name("basic_info_sec").find_element_by_class_name()
        try:
            element = driver.find_element_by_id('mainContents')
            total_height = element.size['height'] + 1000
            driver.set_window_size(1920, total_height)
            time.sleep(1)
            screenshot = element.screenshot_as_png
            image = ImageFile(io.BytesIO(screenshot), name=company_name + '_company_review.png')
            # pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            # with open((path + company_name + '_company_review.png'), 'wb') as f:
            #     f.write(screenshot)
        except Exception as e:
            print("잡플래닛 캡처 실패")
            print(e)
            # 회사 주소 찾기
        try:
            driver.get("https://www.jobplanet.co.kr/companies/"+company_code+"/landing")
            driver.implicitly_wait(5)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            ul = soup.select_one('ul.basic_info_more')
            li = ul.select('dl.info_item_more')[2]
            location = li.select_one('dd').text
            if location=='-':
                location = "장소 없음"
            print(location)
        except Exception as e:
            print("잡플래닛 위치 찾기 실패")
            print(e)

        jobplanet = JobPlanetInfo.objects.get(enter=self.enter)
        jobplanet.company_code = company_code
        jobplanet.upload_to_path = path
        jobplanet.location = location
        jobplanet.url = REVIEW_URL
        jobplanet.save()
        CrwalingPhotos.objects.create(jobplanet_info=jobplanet, photo=image)
        print('잡플래닛 성공')
        driver.quit()
        return location


# jobplanet = GetJobPlanetInfo()
# jobplanet.get_company_info(company_name="쿠팡")

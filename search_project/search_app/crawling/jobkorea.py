import io
import pathlib
import time
import os
from pathlib import Path
from bs4 import BeautifulSoup
from django.core.files.images import ImageFile
from search_app.crawling.crawlselenium import selenium_setting
from search_app.models import CrwalingPhotos, JobKoreaInfo

BASE_URL = "https://www.jobkorea.co.kr/"
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class GetJobKoreaInfo:

    def __init__(self, company_url="", enter=None, count=0):
        self.company_url = company_url
        self.enter = enter
        self.count = count

    def get_company_url(self, URL, driver, company_name):
        driver.get(URL)
        driver.implicitly_wait(5)
        print("현재 주소", driver.current_url)
        href = ""
        try:
            href = driver.find_elements_by_class_name('btn-post-corpinfo')[1].get_attribute('href')
        except:
            print("첫번째 href 없음")
            pass
        if not href:
            try:
                href = driver.find_element_by_class_name('name dev_view')[0].get_attribute('href')
            except:
                print("두번째 href 없음, 다시시도")
                self.count += 1
                if self.count <= 5:
                    print(self.count, "회 진행중입니다 6번째시 넘어갑니다.")
                    self.get_company_info(company_name=company_name)
        return href


    def get_company_info(self, company_name):
        # 기업 정보 페이지로 그대로 가는게 아닌 채용정보쪽의 기업정보라서 (주) 확인 안해도 괜찮음
        print(company_name, '잡코리아 시작')
        driver = selenium_setting()
        href = ""
        company_code = ""
        company_name = company_name.replace(' ', '').replace('\n', '').lstrip('(주)').rstrip('(주)')
        if self.company_url == "":
            URL = "https://www.jobkorea.co.kr/Search/?stext=" + company_name + "&tabType=corp&Page_No=1"
            href = self.get_company_url(URL, driver, company_name)
            company_code = href.split('/')[-1]
            company_url = href + "?tabType=I"
            driver.get(company_url)
        else:
            URL = self.company_url
            company_url = self.company_url
            company_code = URL.split('/')[-1].split('?')[0]
            driver.get(self.company_url)

        print(driver.current_url)
        print(company_code)
        driver.implicitly_wait(5)

        # 이하 데이터 수집
        path = os.path.join(BASE_DIR) + '/media/search_job/' + company_name + '/jobkorea/' + time.strftime(
            "/%Y/%m/%d/")
        try:
            element = driver.find_element_by_class_name('company-body-infomation')
            total_height = element.size['height'] + 1000
            driver.set_window_size(1920, total_height)
            time.sleep(1)
            screenshot = element.screenshot_as_png
            image = ImageFile(io.BytesIO(screenshot), name=company_name + '_company_review.png')
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            th = soup.find_all('th')
            td = soup.find_all('td')
        except Exception as e:
            print("잡코리아 캡처 실패")

        # 주소찾기
        location = ""
        try:
            for index, value in enumerate(th):
                print(index, value.text)
                if value.text == "주소 ":
                    print('주소 찾음')
                    location = td[index].text
                    print(location)
                    break
        except:
            pass

        # 일반 스크린샷 저장용
        # pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        # with open((path + company_name + '_company_review.png'), 'wb') as f:
        #     f.write(screenshot)
        try:
            jobkorea = JobKoreaInfo.objects.get(enter=self.enter)
            jobkorea.company_code = company_code
            jobkorea.company_name = company_name
            jobkorea.upload_to_path = path
            jobkorea.location = location
            jobkorea.url = company_url
            jobkorea.save()
            CrwalingPhotos.objects.create(jobkorea_info=jobkorea, photo=image)
        except Exception as e:
            print("잡코리아 db 저장 실패")
        driver.quit()
        return location


# jobkorea = GetJobKoreaInfo()
# jobkorea.get_company_info("쿠팡")






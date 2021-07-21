import io
import pathlib
import time
import os
from pathlib import Path
from bs4 import BeautifulSoup
from django.core.files.images import ImageFile

from search_app.crawling.crawlselenium import selenium_setting
from search_app.models import KreditJobInfo, CrwalingPhotos
from django.contrib.postgres.fields import ArrayField


class GetKreditJobInfo:
    BASE_URL = "https://www.kreditjob.com/"
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    def __init__(self, company_url="", enter=None, count=0):
        self.company_url = company_url
        self.enter = enter
        self.count = count

    def get_company_url(self, company_name, saramin_location, jobplaent_location, jobkorea_location, driver):

        driver.get(self.BASE_URL)
        print("처음 접속 URL", driver.current_url)
        driver.implicitly_wait(5)
        search = driver.find_element_by_class_name('search-query')
        time.sleep(1)
        search.send_keys(company_name)
        time.sleep(4)
        # 동명회사 거르기 위한 이름이 맞고, 위치가 맞는지 조건문
        try:
            result = driver.find_element_by_class_name("react-autosuggest__suggestions-list")
            result_list = result.find_elements_by_css_selector("[id^=react-autowhatever-1--item-]")
            print("검색결과:",result_list)
            for i in result_list:
                print('result_list 있음')
                name, location = i.text.split('/')
                location1, location2 = location.split(',')
                # 이름에 (주) 말고도 이름(영어이름) 이렇게도 있네 ㅋㅋ
                name = name.rstrip(' ').split('(')[0]
                print(name)
                location1 = location1.lstrip(' ')
                location2 = location2.lstrip(' ')
                print(name, company_name, location1, location2)
                locations1 = {saramin_location[0]:0, jobkorea_location[0]:0, jobplaent_location[0]:0}
                locations2 = {saramin_location[1]:0, jobkorea_location[1]:0, jobplaent_location[1]:0}
                print(locations1, locations2)
                if name == company_name+"(주)" or name == "(주)"+company_name or name in company_name :
                    if location1 in locations1 and location2 in locations2:
                        print("클릭 성공")
                        i.click()
                        driver.implicitly_wait(10)
                        break
            if driver.current_url == "https://www.kreditjob.com/":
                self.count += 1
                print("현재 접속 URL: ", driver.current_url)
                print(self.count, "회 시도중, 찾기 실패, 다시시도 합니다.")
                if self.count <= 5:
                    return self.get_company_url(company_name, saramin_location, jobplaent_location, jobkorea_location, driver)
                else:
                    return True
            else:
                print("찾기 성공")
                print(driver.current_url)
        # TODO: 회사 정상적으로 찾았는데 Exception 걸리는거 수정하기
        except Exception as e:
            print(e)
            print("찾는 회사가 없습니다.")
            self.count += 1
            print(self.count, "회 시도중, 찾기 실패, 다시시도 합니다.")
            if self.count <= 5:
                return self.get_company_url(company_name, saramin_location, jobplaent_location, jobkorea_location, driver)
            else:
                return True
        return False

    def get_company_info(self, company_name, saramin_location="", jobkorea_location="", jobplanet_location=""):
        location = ""
        print(company_name, '크래딧잡 시작')
        driver = selenium_setting()
        jobdam_list = []
        elements = ""
        company_name = company_name.replace(' ', '').replace('\n', '').lstrip('(주)').rstrip('(주)')

        # location 자르기
        if saramin_location:
            s = saramin_location.split(" ")
            saramin_location = [s[0], s[1]]
        else:
            saramin_location = [0, 1]
        if jobkorea_location:
            jk = jobkorea_location.split(" ")
            print(jk)
            jobkorea_location = [jk[0].replace('\n', ''), jk[1]]
            print(jobkorea_location)
        else:
            jobkorea_location = [0, 1]
        if jobplanet_location:
            jp = jobplanet_location.split(" ")
            print(jp)
            jobplanet_location = [jp[0], jp[1]]
            print(jobplanet_location)
        else:
            jobplanet_location = [0, 1]

        # kreditjob은 url을 얻어와서 할수가 없으므로 클릭으로 이동 그러므로 콜만 함
        if self.company_url == "":
            # False면 찾는 회사 있음
            if self.get_company_url(company_name, saramin_location, jobplanet_location, jobkorea_location, driver):
                print("Kreditjob search 실패")
                try:
                    driver.quit()
                except:
                    print("drive가 이미 닫혔습니다.")
                return "Kreditjob search 실패"
        else:
            driver.get(self.company_url)
            driver.implicitly_wait(5)
        url = driver.current_url

        company_code = url.split("/")[-1]
        path = os.path.join(
            self.BASE_DIR) + '/media/search_job/' + company_name + '/kreditjob/' + company_code + time.strftime(
            "/%Y/%m/%d/")
        print(url)
        try:
            # 모든 컨텐츠 캡쳐
            # job담 글 크롤링이 자꾸 no such element가 나와서 캡쳐 후 글 크롤링 진행


            element = driver.find_element_by_class_name('company-contents')
            total_height = element.size['height'] + 1000
            driver.set_window_size(1920, total_height)
            time.sleep(1)
            screenshot = element.screenshot_as_png
            image = ImageFile(io.BytesIO(screenshot), name=company_name + '_company_review.png')
            # pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            # with open((path + company_name + "_" + company_code + '_company_review.png'), 'wb') as f:
            #     f.write(screenshot)
        except Exception as e:
            print("kreditjob 캡처 실패")
            print(e)

        # 크레딧잡 JOB담
        try:
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            info_cell = driver.find_element_by_class_name('info-cell.first')
            location = info_cell.find_element_by_class_name('cat_text').text
            print(location)


            cnt = driver.find_element_by_class_name('d-company-jobdom-header')
            cnt = cnt.find_element_by_class_name('total-cnt').text
            cnt = int(cnt)

            if cnt > 0:
                scroll_times = cnt // 10 + 1
                if scroll_times > 1:
                    for i in range(scroll_times):
                        scroll_element = driver.find_elements_by_class_name('jobdom-post-container')[-1]
                        driver.execute_script("arguments[0].scrollIntoView();", scroll_element);
                        time.sleep(1)

                elements = soup.find_all("div", class_='jobdom-post-container')
                for i in elements:
                    jobdam_dict = {}
                    inner = i.select_one('a')
                    href = inner.attrs['href'][1:]
                    href = self.BASE_URL+href
                    title = inner.select_one('div.title > span.title-label').text
                    date = inner.select_one('span.date').text
                    print(href, title, date)
                    jobdam_dict['href'] = href
                    jobdam_dict['title'] = title
                    jobdam_dict['date'] = date
                    jobdam_list.append(jobdam_dict)
            else:
                print("잡담 갯수 0개 ㅋㅋ")
        except Exception as e:
            print("잡담 크롤링 실패")
            print(e)
        try:
            kreditjob = KreditJobInfo.objects.get(enter=self.enter)
            kreditjob.company_code = company_code
            kreditjob.upload_to_path = path
            kreditjob.url = url
            kreditjob.location = location
            kreditjob.jobdom_list = jobdam_list
            kreditjob.save()
            CrwalingPhotos.objects.create(kreditjob_info=kreditjob, photo=image)
        except Exception as e:
            print("kreditjob DB 넣는 과정에서 에러")
        driver.quit()
        print("크레딧잡까지 성공")


# 크레딧잡은 동일명의 주소를 판별하기위해
# 이전 크롤링에서 얻어온 주소를 바탕으로 비교
# kredit = GetKreditJobInfo()


# saramin = ['서울', '마포구']
# jobplanet = ['서울', '영등포구']
# jobkorea = ['서울', '마포구']
# kredit.get_company_info("블렌딩", saramin, jobplanet, jobkorea)
#
#
# saramin = ['경기', '성남시']
# jobplanet = ['경기', '성남시']
# jobkorea = ['경기', '성남시']
# kredit.get_company_info("네이버", saramin, jobplanet, jobkorea)









import io
import pathlib
import time
import os
from pathlib import Path
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.images import ImageFile

from search_app.crawling.crawlselenium import selenium_setting
from search_app.models import CrwalingModel, SaraminInfo, CrwalingPhotos
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class GetSaraminEnterInfo:

    def __init__(self, company_csn="", company_name="", company_location="", company_url=""):
        self.company_csn = company_csn
        self.company_name = company_name
        self.company_location = company_location
        self.company_url = company_url

    def get_company_url(self, saramin_url, driver):
        company_csn = ""
        company_name = ""
        company_url = ""
        driver.get(saramin_url)
        company_rec_idx = saramin_url.split("=")[-1]
        driver.implicitly_wait(5)
        html = driver.page_source
        if html:
            # 사람인에 기업링크가 없는경우가 있어서 매우 당황스럽다... 흑흑
            try:
                soup = BeautifulSoup(html, 'lxml')
                selector = '#content > div.wrap_jview > div.jview.jview-0-'+company_rec_idx+' > div.wrap_jv_cont > div.wrap_jv_header > div > a.company'
                if not selector:
                    selector = '#content > div.wrap_jview > div > div.wrap_jv_cont > div.wrap_jv_header > div > a.company'

                company_url = soup.select_one(selector).attrs['href']
                company_csn = company_url.split('?')[-1] # cns=~~~ 이렇게 출력됨
        # return {"company_csn": company_csn, "company_name": company_name, "company_url": company_url, "driver": driver}
            except Exception as e:
                print(e)
                print('기업링크가 없습니다.')
        return [company_csn, company_url]

    # TODO get_url은 url만 리턴하고 get_info로 데이터 얻도록 새로 만들기
    def get_company_info(self, saramin_url, company_name):
        print(company_name)
        print("사람인 시작")
        print(saramin_url)
        image1, image2, image3 = "", "", ""
        location = ""
        driver = selenium_setting()

        # 주소가 없으면 url 찾기 실행
        # 여기는 주소가 4개가 있어서 company_csn으로 찾자
        if self.company_csn == "":
            print('DB에서 안불러옴')
            company_csn, company_url = self.get_company_url(saramin_url, driver)
            print(company_csn)
        else:
            company_csn = self.company_csn
            company_name = self.company_name
            company_url = self.company_url
        company_name = company_name.rstrip('(주)').lstrip('(주)')
        
        if settings.DEBUG:
            path = os.path.join(BASE_DIR) + '/media/search_job/'+company_name+'/saramin/' + time.strftime("/%Y/%m/%d/")
        else:
            path = os.path.join(BASE_DIR).lstrip('/') + '/media/search_job/'+company_name+'/saramin/' + time.strftime("%Y/%m/%d")

            # path = 'media/search_job/'+company_name+'/saramin/' + time.strftime("%Y/%m/%d/")
        company_name = company_name.rstrip('(주)').lstrip('(주)')

        # 1. 기업소개 -> 인재채용 -> 연봉정보 -> 재무정보 이 순으로 셀레니움 돌자
        # 없으면 접속이 안된다.. 5초 제한
        # 기업소개 : "https://www.saramin.co.kr/zf_user/company-info/view?"+company_csn
        # 인재채용 : "https://www.saramin.co.kr/zf_user/company-info/view-inner-recruit?"+company_csn
        # 연봉정보 : "https://www.saramin.co.kr/zf_user/company-info/view-inner-salary?"+company_csn
        # 재무정보 : "https://www.saramin.co.kr/zf_user/company-info/view-inner-finance?"+company_csn

        # 기업소개
        url = "https://www.saramin.co.kr/zf_user/company-info"
        # 가끔 모달 띄워서 화면 가리는 경우가 있음
        try:
            driver.find_element_by_class_name('btn_close.ic').click()
            driver.implicitly_wait(5)
        except Exception as e:
            print('화면에 띄워진 Modal 없음')
        # 1. 기업소개
        try:
            driver.get(url + "/view?" + company_csn)
            driver.implicitly_wait(5)
            company_url = driver.current_url
            print(company_name, company_url)
            html = driver.page_source
            if html:
                soup = BeautifulSoup(html, 'lxml')
                # 기업소개 기업개요
                try:
                    company_info_name = soup.select_one('#content > div > div.header_company_view > div.title_company_view > h1 > span.name')
                    company_intro = soup.select_one(
                        '#content > div > div.cont_company_view > div.box_company_view.company_intro')  # 기업소개 상단 div
                    company_info_all = company_intro.select_one('dl.info')
                    # 업종, 대표자명, 홈페이지 기타등등 dl dt dd 이렇게 만들어져있다. mark_safe로 그대로 보여줘야할듯 TODO: 기업정보 가져와서 데이터 저장하기
                    string = ""
                    dd = company_info_all.select('dd')
                    dt = company_info_all.select('dt')
                    for index, value in enumerate(dt):
                        if value.text == "기업주소":
                            location = dd[index].text
                            print(location)
                            break
                except:
                    print("기업위치 불러오기 실패")
            try:
                element = driver.find_element_by_class_name("cont_company_view")
            except:
                try:
                    element = driver.find_element_by_class_name("box_company_view.company_intro")
                except:
                    pass
            print("최대 길이값 찾고")
            total_height = element.size['height'] + 1000
            print("윈도우 사이즈 늘리기")
            driver.set_window_size(1920, total_height)
            time.sleep(1)
            print("스크린샷")
            screenshot1 = element.screenshot_as_png
            print("스크린샷 성공, 이미지 파일로 변환")
            image1 = ImageFile(io.BytesIO(screenshot1), name="company_name" + '_company_info.png')
            print(image1)
            print("성공")
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            with open(path + company_name + company_csn + '_company_info.png', 'wb') as f:
                f.write(screenshot1)

        except Exception as e:
            print(e)
            # 기업소개가 없을수가 있나?
            print('기업소개 없음')

        print("2. 인재채용 넘어감")
        # 2. 인재채용
        # 근데 인재체용은 기업소개에 있긴 하니까... 일단 넘길까
        try:
            pass
            # driver.implicitly_wait(5)
            # driver.get(url+"/view-inner-recruit?"+company_csn)
            # html = driver.page_source
        except Exception as e:
            print(e)
            print('인재채용 없음')

        print("3. 연봉정보")
        # 3. 연봉정보
        try:
            driver.implicitly_wait(5)
            driver.get(url+"/view-inner-salary?" + company_csn)
            element = driver.find_element_by_id('tab_avg_salary')
            total_height = element.size['height'] + 1000
            driver.set_window_size(1920, total_height)
            time.sleep(1)
            screenshot2 = element.screenshot_as_png
            image2 = ImageFile(io.BytesIO(screenshot2), name=company_name + '_company_info_salary.png')
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            with open(path + company_name + company_csn + '_company_info_salary.png', 'wb') as f:
                f.write(screenshot2)
            # html = driver.page_source
            # if html:
            #     soup = BeautifulSoup(html, 'lxml')
            #     avg_salary = soup.select_one('#tab_avg_salary')
            #     graph_salary = avg_salary.select_one('div > div.sri_graph.combie_graph > div')
        except Exception as e:
            print(e)
            print("연봉정보 없음")

        # 4. 재무정보
        print("4. 재무정보")
        try:
            driver.implicitly_wait(5)
            driver.get(url+"/view-inner-finance?"+company_csn)
            element = driver.find_element_by_class_name("cont_company_view.finance")
            total_height = element.size['height'] + 1000
            driver.set_window_size(1920, total_height)
            time.sleep(1)
            screenshot3 = element.screenshot_as_png
            image3 = ImageFile(io.BytesIO(screenshot3), name=company_name + '_company_info_finance.png')
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            with open(path + company_name + company_csn + '_company_info_finance.png', 'wb') as f:
                f.write(screenshot3)
            # pass
            # html = driver.page_source
            # if html:
            #     soup = BeautifulSoup(html, 'lxml')
            #     company_info_dart = soup.select_one('#company_info_dart') # 공시정보 및 보고서

        except Exception as e:
            print(e)
            print("재무정보 없음")
        saramin_company_info_dict = {'company_name': company_name, 'company_csn': company_csn,
                                     'company_url': company_url}
        print("회사 이름", company_name)
        enter = CrwalingModel.objects.create(enter_name=company_name)
        saramin = SaraminInfo.objects.get(enter=enter)
        saramin.company_code = company_csn
        saramin.upload_to_path = path
        saramin.location = location
        saramin.url = company_url
        saramin.save()

        if image1 != "":
            CrwalingPhotos.objects.create(saramin_info=saramin, photo=image1)
        else:
            print("image1 없음")
        if image2 != "":
            CrwalingPhotos.objects.create(saramin_info=saramin, photo=image2)
        else:
            print("image2 없음")
        if image3 != "":
            CrwalingPhotos.objects.create(saramin_info=saramin, photo=image3)
        else:
            print("image3 없음")
        driver.quit()
        return [enter, location]

        # 테스트 전용
        # return location

import time

import requests
import selenium.webdriver
from bs4 import BeautifulSoup
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.support.wait import WebDriverWait


def selenium_setting(saramin_url):
    chromedriver_autoinstaller.install()
    driver_options = webdriver.ChromeOptions()
    driver_options.headless = True
    driver_options.add_argument("--mute-audio")
    driver_options.add_argument('window-size=1920x1080')
    driver_options.add_argument('--disable-gpu')
    driver_options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    # driver_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=driver_options)
    driver.get(saramin_url)
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
    driver.execute_script(
        "const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")
    return driver


def get_saramin_comapny_info(company_csn, driver):
    company_info = {}
    company_info_recruit = {}
    company_info_salary = {}
    company_info_finance = {}
    saramin_company_info_dict = {}

    # 1. 기업소개 -> 인재채용 -> 연봉정보 -> 재무정보 이 순으로 셀레니움 돌자
    # 없으면 접속이 안된다..
    # 근데 이러면 엄청 오래걸리네...
    # 한번 찾을때마다 데이터를 저장하는게 좋을까?
    # 이렇게 4가지가 있는데, 다 있지 않은곳도 있음
    # 기업소개 : "https://www.saramin.co.kr/zf_user/company-info/view?"+company_csn
    # 인재채용 : "https://www.saramin.co.kr/zf_user/company-info/view-inner-recruit?"+company_csn
    # 연봉정보 : "https://www.saramin.co.kr/zf_user/company-info/view-inner-salary?"+company_csn
    # 재무정보 : "https://www.saramin.co.kr/zf_user/company-info/view-inner-finance?"+company_csn

    # 기업소개
    url = "https://www.saramin.co.kr/zf_user/company-info"

    # 1. 기업소개
    try:
        driver.implicitly_wait(0.1)
        driver.get(url + "/view?" + company_csn)
        html = driver.page_source
        if html:
            soup = BeautifulSoup(html, 'lxml')
            # 기업소개 기업개요
            company_intro = soup.select_one(
                '#content > div > div.cont_company_view > div.box_company_view.company_intro')  # 기업소개 상단 div

            company_info_recruits_list = company_intro.select_one('div.recruits > ul.list')  # 채용공고 li로 리스트
            company_info_summary = company_intro.select_one(
                'ul.summary')  # 기업개요 li로 여러개 나옴 업력, 기업형태, 매출액, svg이미지, strong 타이틀, span 텍스트
            company_info_title = company_intro.select_one('div.wrap_detail > p > span').text  # 기업소개 타이틀 text
            company_info_detail = company_intro.select_one('div.wrap_detail > div.detail').text  # 기업소개 글 text
            company_info_all = company_intro.select_one(
                'dl.info')  # 업종, 대표자명, 홈페이지 기타등등 dl dt dd 이렇게 만들어져있다. mark_safe로 그대로 보여줘야할듯 TODO: 기업정보 가져와서 데이터 저장하기
            company_info_gradient = company_intro.select_one('dl.info.vision.gradient').text  # 기업 비전 text
            company_info_welfare = soup.select_one(
                '#content > div > div.cont_company_view > div.box_company_view.company_welfare > ul')  # 기업소개 복리후생 ul, li 리스트

            company_info['company_info_recruits_list'] = company_info_recruits_list
            company_info['company_info_summary'] = company_info_summary
            company_info['company_info_title'] = company_info_title
            company_info['company_info_detail'] = company_info_detail
            company_info['company_info_all'] = company_info_all
            company_info['company_info_gradient'] = company_info_gradient
            company_info['company_info_welfare'] = company_info_welfare

    except Exception as e:
        print(e)
        company_info["response"] = False

    print("2. 인재채용")
    # 2. 인재채용
    # 근데 인재체용은 기업소개에 있긴 하니까... 일단 넘길까
    try:
        pass
        # driver.implicitly_wait(5)
        # driver.get(url+"/view-inner-recruit?"+company_csn)
        # html = driver.page_source
    except Exception as e:
        print(e)
        company_info_recruit["response"] = False

    print("3. 연봉정보")
    # 3. 연봉정보



    try:
        driver.implicitly_wait(5)
        driver.get(url+"/view-inner-salary?" + company_csn)
        screenshot = driver.find_element_by_id('tab_avg_salary').screenshot_as_png
        with open('test.png', 'wb') as f:
            f.write(screenshot)
        pass
        # html = driver.page_source
        # if html:
        #     soup = BeautifulSoup(html, 'lxml')
        #     avg_salary = soup.select_one('#tab_avg_salary')
        #     graph_salary = avg_salary.select_one('div > div.sri_graph.combie_graph > div')
    except Exception as e:
        print(e)
        company_info_salary["response"] = False

    # 4. 재무정보
    print("4. 재무정보")
    try:
        driver.implicitly_wait(5)
        driver.get(url+"/view-inner-finance?"+company_csn)
        html = driver.page_source
    except Exception as e:
        company_info_finance["response"] = False

    return saramin_company_info_dict






def get_saramin_company_url(saramin_url):

    driver = selenium_setting(saramin_url) # 기업정보 페이지 획득
    company_rec_idx = saramin_url.split("=")[-1]
    driver.implicitly_wait(5)
    html = driver.page_source
    if html:
        soup = BeautifulSoup(html, 'lxml')
        # soup = BeautifulSoup(html, 'lxml') 조금더 빠르다고 하는데 체감은 글쎄?
        selector = '#content > div.wrap_jview > div.jview.jview-0-'+company_rec_idx+' > div.wrap_jv_cont > div.wrap_jv_header > div > a.company'
        company_url = soup.select_one(selector).attrs['href']
        company_csn = company_url.split('?')[-1] # cns=~~~ 이렇게 출력됨
        saramin_company_info_dict = get_saramin_comapny_info(company_csn, driver)
        driver.quit()
        return saramin_company_info_dict
    return {"response": "url 수집에 실패했습니다."}


company_url = get_saramin_company_url(saramin_url="https://www.saramin.co.kr/zf_user/jobs/relay/view?view_type=list&rec_idx=40616382")






# jobkorea_url = "https://www.jobplanet.co.kr/companies/382499/reviews/"
#content > div.wrap_jview > div.jview.jview-0-40523925 > div.wrap_jv_cont > div.wrap_jv_header > div > a.company
#content > div.wrap_jview > div.jview.jview-0-40613843 > div.wrap_jv_cont > div.wrap_jv_header > div > a.company

# 사람인 기업정보 크롤링
# 0. 취업정보 링크 필수
# 취업정보 링크로 들어가서 기업정보 링크 따야함
# 이후 기업정보
# 기업소개 -> 인재채용 -> 연봉정보 -> 재무정보순서


# 이하 사람인 기업정보 링크 2개의 방법
# 1. 최상단 기업정보 url
# 기업정보 상위 url
#content > div.jview_floating.jview > div > div.jv_header_float > div > a.company

# 2. 하단 기업정보 url
#content > div.wrap_jview > div.jview.jview-0-40616382 > div.wrap_jv_cont > div.jv_cont.jv_company
#content > div.wrap_jview > div.jview.jview-0-40616179 > div.wrap_jv_cont > div.jv_cont.jv_company

# 2번 주의사항
# content > div.wrap_jview > div.jview.jview-0-40615590 > div.wrap_jv_cont > div.jv_cont.jv_company > div.cont.box > div > div.title > a
# 코드 보면 이 구조가 맞는데...

# content > div.wrap_jview > div.jview.jview-0-40616382 > div.wrap_jv_cont > div.jv_cont.jv_company > div:nth-child(2) > div.wrap_info > div.title > a:nth-child(3)
# 이렇게 나오는건 또 뭐야... child는 왜 나옴? 한번 테스트 해봐야 할듯

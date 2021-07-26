import requests
import pickle
from bs4 import BeautifulSoup


def SearchJob(context, page, search_job):
    saramin_url = "https://www.saramin.co.kr/zf_user/jobs/list/domestic?" \
                  "loc_mcd=101000%2C102000&" \
                  "page=" + page + "&" \
                                   "searchType=search" \
                                   "&searchword=" + search_job + "&" \
                                                                 "exp_cd=1&" \
                                                                 "&edu_min=7&edu_max=10" \
                                                                 "edu_min=7&edu_max=10&edu_none=y&" \
                                                                 "search_optional_item=y&search_done=y&panel_count=y&sort=RD&tab_type=all&" \
                                                                 "loc_nm%5B101000%5D=%EC%84%9C%EC%9A%B8%EC%A0%84%EC%B2%B4&loc_nm%5B102000%5D=%EA%B2%BD%EA%B8%B0%EC%A0%84%EC%B2%B4&" \
                                                                 "isSearchResultEmpty=true&isSectionHome=false&searchParamCount=6&recruit_kind=recruit&quick_apply=n"

    # 경력 : exp_cd=1
    # 지역 : loc_mcd=101000%2C102000
    # 검색 : searchword=
    # 사람인 API 가이드 "https://oapi.saramin.co.kr/guide/job-search-id" 확인
    jobkorea_url = ""
    response = requests.get(saramin_url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        # soup = BeautifulSoup(html, 'lxml') 조금더 빠르다고 하는데 체감은 별로...
        body = soup.select('#default_list_wrap > section > div.list_body > div')
        page_cal = 1

        # 공고 개수
        # 개수마다 찾아지는게 달라진다 :(
        if int(page) <= 1:
            try:
                count = soup.select_one(
                    '#content > div.recruit_list_renew > div.common_recruilt_list > div.area_title.list_total_count > span > em').text
                page_cal = int(count.replace(",", "")) // 50
            except:
                context['count'] = 0
                return context
        else:
            try:
                count = soup.select_one('#list_tab > li.tab.on > a > span').text.rstrip(")").replace("(", "").rstrip(
                    "건")
                page_cal = int(count.replace(",", "")) // 50
            except:
                context['count'] = 0
                return context

        list = []

        # 공고 내용들 리스트 및 context 넣기
        try:
            for i in body:
                context = {}
                id = i.get('id', 'null')
                company = i.select_one('div > div.col.company_nm > a > span').text
                company = company.replace(' ', '').replace('\n', '').lstrip('(주)').rstrip('(주)').strip().split('(')[0]
                href = i.select_one('div > div.col.company_nm > a').attrs['href']
                title = i.select_one('div > div.col.notification_info > div.job_tit > a > span').text
                career = i.select_one('div > div.col.recruit_condition > p.career').text
                education = i.select_one('div > div.col.recruit_condition > p.education').text
                employment_type = i.select_one('div > div.col.company_info > p.employment_type').text
                work_place = i.select_one('div > div.col.company_info > p.work_place').text
                deadlines = i.select_one('div > div.col.support_info > p.deadlines').text
                reg_date = i.select_one('div > div.col.support_info > p.deadlines > span.reg_date').text
                context['id'] = id
                context['company'] = company
                context['href'] = href
                context['title'] = title
                context['career'] = career
                context['education'] = education
                context['employment_type'] = employment_type
                context['work_place'] = work_place
                context['deadlines'] = deadlines
                context['reg_date'] = reg_date
                list.append(context)
            context['job_list'] = list
            context['count'] = count
        except:
            pass
        context['page_cal'] = page_cal + 1
        context['last_q'] = search_job
        try:
            foo = pickle.load(open("var.pickle", "rb"))
        except (OSError, IOError) as e:
            foo = 3
            pickle.dump(foo, open("var.pickle", "wb"))
            # context.decode('utf8')
            # print(context)
        return context
    return {context:""}

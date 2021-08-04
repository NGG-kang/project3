# project3
 채용공고 크롤링(사람인) 및 기업정보(사람인, 잡플래닛, 크래딧잡) 크롤링

아직 진행중인 프로젝트입니다.

트렐로 참조 https://trello.com/b/IWwCXDoJ/project3

배포된 주소 https://mixedprogramming.net/search_job/ (기본 빈 주소는 api입니다)

프로젝트 소개 https://vintage-dollar-2cf.notion.site/ec6efd52500b4c43bfe9fbc87c0c8e98



## 설치

**주의사항**

환경설정, 시크릿키가 빠져있는 상태입니다.

설치하셔도 실행이 안됩니다.

`docker-compose up -- build`





## 기술스택

언어: python

프레임워크: Django

배포: Docker, Docker-compose, AWS-ec2

AWS: EC2(배포용), RDS(postgres), ElastiCache(Redis, Memcache), S3(static, media)

주 사용 라이브러리 : Celery, Crontab, Selenium, Beautifulsoup








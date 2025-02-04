# -*- coding: utf-8 -*-
"""
네이버 뉴스 검색 결과에서 기사 링크를 추출하고,
각 뉴스 기사에 달린 댓글을 수집하여 하나의 엑셀 파일로 저장하는 코드임.
"""

# ===== 라이브러리 임포트 =====
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import requests
import re
from tqdm import tqdm
import pandas as pd
import datetime
# ===== 함수 정의 =====

def makePgNum(num):
    """
    검색 결과 페이지에서 start 파라미터에 들어갈 숫자를 생성함.
    예) 1페이지 → 1, 2페이지 → 11, 3페이지 → 21, ...
    """
    if num <= 1:
        return 1
    else:
        return num + 9 * (num - 1)

def convert_naver_news_url(mobile_url):
    """
    모바일 뉴스 URL을 데스크탑 뉴스 URL 형식으로 변환함.
    예) '/mnews/article/015/0004941038?sid=101' → 데스크탑용 URL
    """
    parsed_url = urlparse(mobile_url)
    path_parts = parsed_url.path.split('/')
    
    if len(path_parts) < 5:
        raise ValueError("올바른 모바일 뉴스 URL 형식이 아님.")
    
    oid = path_parts[3]
    aid = path_parts[4]
    
    query_params = parse_qs(parsed_url.query)
    mobile_sid = query_params.get('sid', [''])[0]
    if mobile_sid:
        try:
            desktop_sid = str(int(mobile_sid) - 1)
        except ValueError:
            desktop_sid = mobile_sid
    else:
        desktop_sid = ''
    
    new_netloc = "news.naver.com"
    new_path = "/main/read.naver"
    new_query_params = {
        "mode": "LSD",
        "mid": "shm",
        "sid1": desktop_sid,
        "oid": oid,
        "aid": aid
    }
    new_query = urlencode(new_query_params)
    desktop_url = urlunparse(('https', new_netloc, new_path, '', new_query, ''))
    return desktop_url

def makeUrl(search, start_pg, end_pg):
    """
    검색어와 시작/종료 페이지를 받아 네이버 뉴스 검색 URL(들)을 생성함.
    - 한 페이지만 검색할 경우: 문자열 하나 반환
    - 여러 페이지일 경우: URL 리스트 반환
    """
    base_url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query="
    if start_pg == end_pg:
        start_num = makePgNum(start_pg)
        return f"{base_url}{search}&start={start_num}"
    else:
        urls = []
        for i in range(start_pg, end_pg + 1):
            start_num = makePgNum(i)
            urls.append(f"{base_url}{search}&start={start_num}")
        return urls

def news_attrs_crawler(elements, attr_name):
    """
    BeautifulSoup 객체에서 추출한 요소들의 특정 속성(attr_name) 값을 리스트로 반환함.
    """
    return [elem.attrs[attr_name] for elem in elements]

# 네이버 서버와의 연결 시 사용할 헤더 (ConnectionError 예방)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"
}

def articles_crawler(page_url):
    """
    검색 결과 페이지의 URL을 받아 뉴스 기사 링크들을 추출하여 리스트로 반환함.
    CSS 선택자를 이용하여 뉴스 링크 요소들을 찾음.
    """
    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    news_link_elements = soup.select("div.group_news > ul.list_news > li div.news_area > div.news_info > div.info_group > a.info")
    links = news_attrs_crawler(news_link_elements, 'href')
    return links

def get_df(article_url):
    """
    데스크탑 뉴스 URL을 입력받아 해당 기사 댓글을 수집한 후,
    '기사댓글'과 '기사링크' 컬럼을 가진 DataFrame을 반환함.
    댓글은 네이버 댓글 API를 통해 수집함.
    """
    try:
        oid = article_url.split("oid=")[1].split("&")[0]
        aid = article_url.split("aid=")[1]
    except IndexError:
        raise ValueError("기사 URL에서 oid 또는 aid를 추출할 수 없음.")
    
    all_comments = []
    page = 1
    comment_header = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "referer": article_url,
    }
    
    while True:
        c_url = (
            "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?"
            "ticket=news&templateId=default_society&pool=cbox5"
            "&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country="
            f"&objectId=news{oid}%2C{aid}"
            "&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT"
            "&pageType=more&page=" + str(page) +
            "&refresh=false&sort=FAVORITE"
        )
        r = requests.get(c_url, headers=comment_header)
        
        soup = BeautifulSoup(r.content, "html.parser")
        content_str = str(soup)
        
        try:
            total_comm = int(content_str.split('comment":')[1].split(",")[0])
        except (IndexError, ValueError):
            total_comm = 0
        
        matches = re.findall(r'"contents":"(.*?)","userIdNo"', content_str)
        all_comments.extend(matches)
        
        if total_comm <= (page * 20):
            break
        else:
            page += 1

    df = pd.DataFrame(all_comments, columns=["기사댓글"])
    df["기사링크"] = article_url
    df = df.reset_index(drop=True)
    return df

# ===== 메인 실행 부분 =====

if __name__ == "__main__":
    search = input("검색할 키워드를 입력해주세요: ")
    start_page = int(input("크롤링할 시작 페이지를 입력해주세요 (숫자만 입력): "))
    end_page = int(input("크롤링할 종료 페이지를 입력해주세요 (숫자만 입력): "))
    print(f"\n검색어: {search}, 페이지: {start_page} ~ {end_page}")
    
    search_urls = makeUrl(search, start_page, end_page)
    if isinstance(search_urls, str):
        search_urls = [search_urls]
    
    news_urls_nested = []
    for page_url in tqdm(search_urls, desc="검색 결과 페이지 처리"):
        links = articles_crawler(page_url)
        news_urls_nested.append(links)
    
    all_news_urls = []
    for sublist in news_urls_nested:
        all_news_urls.extend(sublist)
    
    final_urls = [link for link in all_news_urls if "news.naver.com" in link]
    print(f"\n최종 기사 링크 개수: {len(final_urls)}")
    
    all_comments_dfs = []
    for news_link in tqdm(final_urls, desc="기사별 댓글 수집"):
        article_url = convert_naver_news_url(news_link)
        try:
            df = get_df(article_url)
            all_comments_dfs.append(df)
        except Exception as e:
            print(f"오류 발생 ({article_url}): {e}")
    
    if all_comments_dfs:
        final_comments_df = pd.concat(all_comments_dfs, ignore_index=True)
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 파일명에 날짜시간을 추가하여 고유한 파일명 생성
        filename = f"all_news_comments_{search}_{now}.xlsx"
        
        # 엑셀 파일 저장
        final_comments_df.to_excel(filename, index=False)
        print("수집완료. 파일명 :"+filename)
    else:
        print("수집된 댓글이 없음.")


# Naver News Comment Crawler 📰💬

이 프로젝트는 **네이버 뉴스 검색 결과**에서 기사 링크를 추출하고, 각 기사에 달린 **댓글**을 수집하여 **엑셀 파일**로 저장하는 Python 스크립트입니다.

## 📦 기능
- 네이버 뉴스 검색 결과에서 **기사 링크** 자동 수집.
- 각 기사에 달린 **댓글** 수집.
- 수집한 댓글과 기사 링크를 **엑셀 파일**(`all_news_comments.xlsx`)로 저장.

## 🔧 사용 방법

1. **스크립트 실행**
   ```bash
   python naver_news_comment_crawler.py
   ```

2. **입력값 제공**
   - `검색할 키워드` 입력
   - `시작 페이지` 및 `종료 페이지` 입력 (숫자만)

3. **결과 확인**
   - 스크립트 실행 후 `all_news_comments.xlsx` 파일이 생성됨.
   - 파일에는 `기사댓글`과 `기사링크` 컬럼이 포함됨.

## 📂 예시
1. **키워드 입력**:  
   ```
   검색할 키워드를 입력해주세요: 인공지능
   크롤링할 시작 페이지를 입력해주세요 (숫자만 입력): 1
   크롤링할 종료 페이지를 입력해주세요 (숫자만 입력): 2
   ```

2. **결과 파일**:  
   `all_news_comments.xlsx` 파일이 생성되며, 다음과 같은 내용이 포함됨.

   | 기사댓글                      | 기사링크                                                                 |
   |-------------------------------|--------------------------------------------------------------------------|
   | 인공지능이 정말 대단하네요!    | https://news.naver.com/main/read.naver?mode=LSD&mid=shm&sid1=101&oid=001&aid=0000000001 |
   | 너무 빠르게 발전하는 것 같아요 | https://news.naver.com/main/read.naver?mode=LSD&mid=shm&sid1=101&oid=001&aid=0000000002 |

---

## 🔍 주요 함수 설명

### 1. `makePgNum(num)`
- **기능**: 검색 결과 페이지 번호를 start 파라미터로 변환함.
- **예시**:  
  - 1페이지 → 1  
  - 2페이지 → 11  
  - 3페이지 → 21

---

### 2. `makeUrl(search, start_pg, end_pg)`
- **기능**: 검색어와 페이지 번호를 받아 네이버 뉴스 검색 URL 생성.
- **반환**: 한 페이지면 문자열, 여러 페이지면 URL 리스트 반환.

---

### 3. `articles_crawler(page_url)`
- **기능**: 주어진 검색 결과 페이지 URL에서 **뉴스 기사 링크** 추출.
- **반환**: 뉴스 기사 링크 리스트.

---

### 4. `get_df(article_url)`
- **기능**: 기사 URL을 입력받아 해당 기사에 달린 **댓글**을 수집하고 DataFrame 반환.
- **반환**: `기사댓글`, `기사링크` 컬럼을 가진 DataFrame.

---

## ⚠️ 주의사항
- **네이버 API 변경**이나 **페이지 구조 변경** 시 코드가 정상 작동하지 않을 수 있습니다.




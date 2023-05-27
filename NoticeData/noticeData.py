import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup


def post_filter(string):
    return not string.isspace() and len(string) > 0 and not '\r' in string


def get_post_contents(bulletin, postNumber):
    bulletinDict = {'일반': 14, '장학': 15, '학사': 16}
    url = 'https://portal.koreatech.ac.kr/ctt/bb/bulletin?b=' + str(bulletinDict[bulletin]) + '&p=' + str(postNumber)
    response = requests.get(url)
    result = ''
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.select_one('#bi_cont_middle > div:nth-child(7) > div')
        result = str(div)
        # context = BeautifulSoup(str(div), 'lxml').text
        # content = soup.select('p')

    else:
        print(response.status_code)
    return result, url


def get_post_list(bulletin, page):
    now = datetime.now()
    bulletinDict = {'일반': 14, '장학': 15, '학사': 16}
    url = 'https://portal.koreatech.ac.kr/ctt/bb/bulletin?b=' + str(bulletinDict[bulletin]) + '&ln=' + str(page)
    response = requests.get(url)
    subList = []
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        tr = soup.select('tr')
        isFirst = True
        for r in tr:
            if isFirst:
                isFirst = False
                continue
            post = (r.text.split('\n'))
            post = (list(filter(post_filter, post)))
            for j in range(0, len(post)):
                post[j] = post[j].strip(' ')
            if (bulletin == '일반'):
                postDate = datetime.strptime(post[3], '%Y-%m-%d')
                if (now - postDate).days <= 180:
                    postDict = {}
                    postDict['postNumber'] = post[0]
                    postDict['postTitle'] = post[2]
                    postDict['postDate'] = post[3]
                    postDict['postWriter'] = post[4]
                    postDict['postContent'], postDict['postLink'] = get_post_contents(bulletin, post[0])
                    subList.append(postDict)
            else:
                postDate = datetime.strptime(post[2], '%Y-%m-%d')
                if (now - postDate).days <= 180:
                    postDict = {}
                    postDict['postNumber'] = post[0]
                    postDict['postTitle'] = post[1]
                    postDict['postDate'] = post[2]
                    postDict['postWriter'] = post[3]
                    postDict['postContent'], postDict['postLink'] = get_post_contents(bulletin, post[0])
                    subList.append(postDict)
    else:
        print(response.status_code)
    return subList


def get_post_list_range(bulletin, start, end):
    crawlingList = []
    for i in range(start, end + 1):
        crawlingList += get_post_list(bulletin, i)
    return crawlingList


def get_180days_post_list(bulletin):
    lastCrawling = []
    crawlingList = []
    i = 1
    while True:
        crawling = get_post_list(bulletin, i)
        if (crawling == lastCrawling):
            break
        else:
            lastCrawling = crawling
            crawlingList += lastCrawling
    return lastCrawling


# 시작페이지부터 종료페이지사이 범위의 게시글 목록 json 배열로 반환, 180일 이내 게시글만 반환
# postNumber : 글 번호
# postTitle : 글 제목
# postDate : 등록일
# postWriter : 작성자
# postContent : 글 내용(html 태그 포함)

# bulletin : '일반', '장학', '학사'
# start : 크롤링할 범위의 시작 페이지(포함)
# end : 크롤링할 범위의 마지막 페이지(포함)
def get_post_json_range(bulletin, start, end):
    return json.dumps(get_post_list_range(bulletin, start, end), indent='\t', ensure_ascii=False)


# 특정 게시판의 180일 간의 게시글 목록 json 배열로 반환
# postNumber : 글 번호
# postTitle : 글 제목
# postDate : 등록일
# postWriter : 작성자
# postContent : 글 내용(html 태그 포함)
#
# 파라미터
# bulletin : '일반', '장학', '학사'
def get_180days_post_json(bulletin):
    return json.dumps(get_180days_post_list(bulletin), indent='\t', ensure_ascii=False)


# 모든(일반공지, 장학공지, 학사공지) 게시판의 180일 간의 게시글 목록 json 배열로 반환
# postNumber : 글 번호
# postTitle : 글 제목
# postDate : 등록일
# postWriter : 작성자
# postContent : 글 내용(html 태그 포함)
def get_180dats_all_post_json():
    result = []
    result += get_180days_post_list('일반')
    result += get_180days_post_list('학사')
    result += get_180days_post_list('장학')
    with open('notice.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent='\t', ensure_ascii=False)
    return json.dumps(result, indent='\t', ensure_ascii=False)


if __name__ == '__main__':
    get_180dats_all_post_json()
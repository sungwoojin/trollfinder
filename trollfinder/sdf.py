import json
import os
import re
import urllib.request
import time
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template
from urllib import parse
from string import punctuation

app = Flask(__name__)

slack_token = ""
slack_client_id = ""
slack_client_secret = ""
slack_verification = ""

sc = SlackClient(slack_token)


# 크롤링 함수 구현하기
def _crawl_troll_man(text):
    # 한글 이름과 영문 이름 매칭할 딕셔너리가 필요함
    nameDict = {'아트록스': 'aatrox', '아리': 'ahri', '아칼리': 'akali', '알리스타': 'alistar', '아무무': 'amumu', '애니비아': 'anivia',
                '애니': 'annie', '애쉬': 'ashe', '아우렐리온솔': 'aurelionsol', '아지르': 'azir', '바드': 'bard',
                '블리츠크랭크': 'blitzcrank',
                '브랜드': 'brand', '브라움': 'braum', '케이틀린': 'caitlyn', '카밀': 'camille', '카시오페아': 'cassiopeia',
                '초가스': 'chogath',
                '코르키': 'corki', '다리우스': 'darius', '다이애나': 'diana', '문도박사': 'drmundo', '드레이븐': 'draven', '에코': 'ekko',
                '엘리스': 'elise',
                '이블린': 'evelynn', '이즈리얼': 'ezreal', '피들스틱': 'fiddlesticks', '피오라': 'fiora', '피즈': 'fizz',
                '갈리오': 'galio',
                '갱플랭크': 'gangplank', '가렌': 'garen', '나르': 'gnar', '그라가스': 'gragas', '그레이브즈': 'graves', '헤카림': 'hecarim',
                '하이머딩거': 'heimerdinger', '일라오이': 'illaoi', '이렐리아': 'irelia', '아이번': 'ivern', '잔나': 'janna',
                '자르반4세': 'jarvaniv',
                '잭스': 'jax', '제이스': 'jayce', '진': 'jhin', '징크스': 'jinx', '카이사': 'kaisa', '칼리스타': 'kalista',
                '카르마': 'karma',
                '카서스': 'karthus', '카사딘': 'kassadin', '카타리나': 'katarina', '케일': 'kayle', '케인': 'kayn', '케넨': 'kennen',
                '카직스': 'khazix',
                '킨드레드': 'kindred', '클레드': 'kled', '코그모': "kog'maw", '르블랑': 'leblanc', '리신': 'lee sin', '레오나': 'leona',
                '리산드라': 'lissandra', '루시안': 'lucian', '룰루': 'lulu', '럭스': 'lux', '말파이트': 'malphite', '말자하': 'malzahar',
                '마오카이': 'maokai', '마스터이': 'masteryi', '미스포츈': 'missfortune', '모데카이저': 'mordekaiser', '모르가나': 'morgana',
                '나미': 'nami',
                '나서스': 'nasus', '노틸러스': 'nautilus', '니코': 'neeko', '니달리': 'nidalee', '녹턴': 'nocturne', '누누와윌럼프': 'nunu',
                '올라프': 'olaf',
                '오리아나': 'orianna', '오른': 'ornn', '판테온': 'pantheon', '뽀삐': 'poppy', '파이크': 'pyke', '퀸': 'quinn',
                '라칸': 'rakan', '람머스': 'rammus',
                '렉사이': 'reksai', '레넥톤': 'renekton', '렝가': 'rengar', '리븐': 'riven', '럼블': 'rumble', '라이즈': 'ryze',
                '세주아니': 'sejuani',
                '샤코': 'shaco', '쉔': 'shen', '쉬바나': 'shyvana', '신지드': 'singed', '사이온': 'sion', '시비르': 'sivir',
                '스카너': 'skarner', '소나': 'sona',
                '소라카': 'soraka', '스웨인': 'swain', '신드라': 'syndra', '탐켄치': 'tahmkench', '탈리아': 'taliyah', '탈론': 'talon',
                '타릭': 'taric',
                '티모': 'teemo', '쓰레쉬': 'thresh', '트리스타나': 'tristana', '트런들': 'trundle', '트린다미어': 'tryndamere',
                '트위스티드페이트': 'twistedfate',
                '트위치': 'twitch', '우디르': 'udyr', '우르곳': 'urgot', '바루스': 'varus', '베인': 'vayne', '베이가': 'veigar',
                '벨코즈': 'velkoz', '바이': 'vi',
                '빅토르': 'viktor', '블라디미르': 'vladimir', '볼리베어': 'volibear', '워윅': 'warwick', '오공': 'wukong',
                '자야': 'xayah', '제라스': 'xerath',
                '신짜오': 'xinzhao', '야스오': 'yasuo', '요릭': 'yorick', '자크': 'zac', '제드': 'zed', '직스': 'ziggs',
                '질리언': 'zilean', '조이': 'zoe', '자이라': 'zyra'}

    originNameDict = {'아트록스': 'Aatrox', '아리': 'Ahri', '아칼리': 'Akali', '알리스타': 'Alistar', '아무무': 'Amumu',
                      '애니비아': 'Anivia', '애니': 'Annie', '애쉬': 'Ashe', '아우렐리온솔': 'Aurelion Sol', '아지르': 'Azir',
                      '바드': 'Bard', '블리츠크랭크': 'Blitzcrank', '브랜드': 'Brand', '브라움': 'Braum', '케이틀린': 'Caitlyn',
                      '카밀': 'Camille', '카시오페아': 'Cassiopeia', '초가스': "Cho'Gath", '코르키': 'Corki', '다리우스': 'Darius',
                      '다이애나': 'Diana', '문도박사': 'Dr. Mundo', '드레이븐': 'Draven', '에코': 'Ekko', '엘리스': 'Elise',
                      '이블린': 'Evelynn', '이즈리얼': 'Ezreal', '피들스틱': 'Fiddlesticks', '피오라': 'Fiora', '피즈': 'Fizz',
                      '갈리오': 'Galio', '갱플랭크': 'Gangplank', '가렌': 'Garen', '나르': 'Gnar', '그라가스': 'Gragas',
                      '그레이브즈': 'Graves', '헤카림': 'Hecarim', '하이머딩거': 'Heimerdinger', '일라오이': 'Illaoi',
                      '이렐리아': 'Irelia', '아이번': 'Ivern', '잔나': 'Janna', '자르반4세': 'Jarvan IV', '잭스': 'Jax',
                      '제이스': 'Jayce', '진': 'Jhin', '징크스': 'Jinx', '카이사': "Kai'Sa", '칼리스타': 'Kalista', '카르마': 'Karma',
                      '카서스': 'Karthus', '카사딘': 'Kassadin', '카타리나': 'Katarina', '케일': 'Kayle', '케인': 'Kayn',
                      '케넨': 'Kennen', '카직스': "Kha'Zix", '킨드레드': 'Kindred', '클레드': 'Kled', '코그모': "Kog'Maw",
                      '르블랑': 'LeBlanc', '리신': 'Lee Sin', '레오나': 'Leona', '리산드라': 'Lissandra', '루시안': 'Lucian',
                      '룰루': 'Lulu', '럭스': 'Lux', '말파이트': 'Malphite', '말자하': 'Malzahar', '마오카이': 'Maokai',
                      '마스터이': 'Master Yi', '미스포츈': 'Miss Fortune', '모데카이저': 'Mordekaiser', '모르가나': 'Morgana',
                      '나미': 'Nami', '나서스': 'Nasus', '노틸러스': 'Nautilus', '니코': 'Neeko', '니달리': 'Nidalee',
                      '녹턴': 'Nocturne', '누누와윌럼프': 'Nunu & Willump', '올라프': 'Olaf', '오리아나': 'Orianna',
                      '오른': 'Ornn', '판테온': 'Pantheon', '뽀삐': 'Poppy', '파이크': 'Pyke', '퀸': 'Quinn', '라칸': 'Rakan',
                      '람머스': 'Rammus', '렉사이': "Rek'Sai", '레넥톤': 'Renekton', '렝가': 'Rengar', '리븐': 'Riven', '럼블': 'Rumble',
                      '라이즈': 'Ryze', '세주아니': 'Sejuani', '샤코': 'Shaco', '쉔': 'Shen', '쉬바나': 'Shyvana', '신지드': 'Singed',
                      '사이온': 'Sion', '시비르': 'Sivir', '스카너': 'Skarner', '소나': 'Sona', '소라카': 'Soraka', '스웨인': 'Swain',
                      '신드라': 'Syndra', '탐켄치': 'Tahm Kench', '탈리아': 'Taliyah', '탈론': 'Talon', '타릭': 'Taric', '티모': 'Teemo',
                      '쓰레쉬': 'Thresh', '트리스타나': 'Tristana', '트런들': 'Trundle', '트린다미어': 'Tryndamere',
                      '트위스티드페이트': 'Twisted Fate', '트위치': 'Twitch', '우디르': 'Udyr', '우르곳': 'Urgot',
                      '바루스': 'Varus', '베인': 'Vayne', '베이가': 'Veigar', '벨코즈': "Vel'Koz", '바이': 'Vi', '빅토르': 'Viktor',
                      '블라디미르': 'Vladimir', '볼리베어': 'Volibear', '워윅': 'Warwick', '오공': 'Wukong', '자야': 'Xayah',
                      '제라스': 'Xerath', '신짜오': 'Xin Zhao', '야스오': 'Yasuo', '요릭': 'Yorick',
                      '자크': 'Zac', '제드': 'Zed', '직스': 'Ziggs', '질리언': 'Zilean', '조이': 'Zoe', '자이라': 'Zyra'}

    lineDict = {'Top': 0, "Jungle": 1, "Middle": 2, "Bottom": 3, "Support": 4}
    lineHangul = {"탑": 'Top', "정글": 'Jungle', "미드": "Middle", "바텀": "Bottom", "서포터": "Support"}

    dataList = text.split()  # 입력은 '성우진 탑 베인' 과 같이 받음
    if (len(dataList) != 4):
        msg = "잘못 입력되었습니다. <아이디> <라인> <챔프> 의 형식으로 입력해주세요." \
              "\n각 항목은 띄어쓰기 없이 입력하셔야 합니다." \
              "\n라인 별 디폴트 명칭 : 탑, 정글, 미드, 바텀, 서포터" \
              "\nex) hideonbush 탑 아우렐리온솔"
    else:
        playerID = parse.quote(dataList[1])  # 그 데이터 각각을 넣어줌
        playerLine = lineHangul[dataList[2]]  # 사용자에게 입력받은 트롤러의 현재 라인을 한글->영문으로 변경
        playerChamp = dataList[3]  # 트롤러의 챔피언을 한글로 받음

        # 챔피언 분석 페이지로 들어가기 (해당 페이지에서, 그 챔프가 분류된 라인을 알고 싶으니까)
        champUrl = 'http://www.op.gg/champion/statistics/'

        sourcecode = urllib.request.urlopen(champUrl).read()
        soup = BeautifulSoup(sourcecode, "html.parser")  # 여기까지 데이터 불러오기 완료

        # a 로 시작하는 모든 코드들 가져옴
        fullcode = soup.select("a")

        # 해당 챔프의 정석 라인을 저장할 리스트 생성
        lineList = []

        for champData in fullcode:
            if '/champion/' + nameDict[playerChamp] + '/statistics' in str(champData):
                nameResult = champData.find(class_="champion-index__champion-item__name")
                nameResult = str(nameResult)[49:-6]
                # print(nameResult)
                # indexLen = champData.find(class_="champion-index__champion-item__positions")
                # indexLen = len(indexLen)

                for line in champData.find_all(class_="champion-index__champion-item__position"):
                    lineList.append(str(line)[59:-13])

                # 여기까지 챔프별 정석 라인 구했음
                # print("정석 라인 : ", lineList)

        # 정석 판단하기
        if lineHangul[dataList[2]] in lineList:
            msg = "이 유저는 [정석]으로 플레이중입니다만...?\n" \
                  "혹시... 이 유저가 트롤이라고 믿고 싶은 당신의 마음이 트롤인 것은 아닐까요..?"

        else:  # 정석이 아닐 경우 분석 들어가야함

            matchUrl = "http://www.op.gg/summoner/userName=" + str(playerID)

            sourcecode = urllib.request.urlopen(matchUrl).read()
            soup = BeautifulSoup(sourcecode, "html.parser")  # 여기까지 데이터 불러오기 완료

            fullcode = soup.select("div")

            matchuserList = []
            matchResult = []

            matchCount = 0
            for matchData in fullcode:
                for mData in matchData.find_all(class_="GameItemWrap"):  # 경기 별
                    # 승리 데이터 저장
                    if matchCount == 20:
                        break
                    # print(matchResult)
                    temp = mData.find(class_="GameResult")
                    temp = str(temp).strip()
                    # print(temp)
                    matchResult.append(temp)
                    matchCount = matchCount + 1

                    for myTeam in mData.find_all(class_="FollowPlayers Names"):  # 해당 mData(경기 1개)의 내용 중 유저 10명이 출력됨
                        matchuserList.append(myTeam.find_all(class_="Summoner"))

                if matchCount == 20:
                    break

            trollCount = 0
            vicCount = 0

            count = 0
            index = 0

            for matchuser in matchuserList:  # matchuserList : 20경기 전체의 플레이어 리스트
                # 그 중에 matchuser 라는건, 20 경기중 한 경기의 유저 10명의 리스트
                finalcount = 0
                for user in matchuser:
                    if "Summoner Requester" in str(user):
                        uppername = originNameDict[playerChamp]
                        if uppername in str(user):
                            finalcount = count % 5  # op.gg 상에서의 나의 최종 위치

                            print("FINAL COUNT: ", finalcount)
                            count = 0
                            break
                    else:
                        count = count + 1
                count = 0

                # lineDict = {'Top': 0, "Jungle": 1, "Middle": 2, "Bottom": 3, "Support": 4}

                # 맨 처음 입력 받은 라인과, 이 사람이 실제 선 라인이 같은지를 판단해서, 맞는 게임의 횟수 추출
                # 즉 트롤 한 경우
                if (finalcount == lineDict[playerLine]):  # 내가 최종적으로 위치한 라인 == 맨 처음 입력한 라인의 고유 번호
                    trollCount = trollCount + 1
                    if 'Victory' in matchResult[index]:
                        vicCount = vicCount + 1
                index = index + 1

            print("승리 카운트 : ", vicCount)
            print("트롤 카운트 : ", trollCount)

            if(trollCount == 0):
                msg = "최근 20 경기 내에서 결과를 찾을 수 없습니다.\n"

            else:
                finalResult = (vicCount / float(trollCount)) * 100

                msg = "이 유저의 최근 20 경기 중, 지금의 픽과 유사한 게임은 %d 게임으로 판단됩니다.\n" \
                      "그 중 승리한 경기는 %d 게임이네요. 즉, 승률은 %0.2f%% 입니다.\n\n" % (trollCount, vicCount, finalResult)

                if finalResult >= 70:
                    msg = msg + "이렇게 [잘하는 사람]을 트롤이라고 의심한, 당신의 마음이 트롤인 것은 아닐까요..?"
                elif finalResult > 35 and finalResult < 70:
                    msg = msg + "이 사람은 판단하기 [애매한 사람] 이네요. 한 번 믿고 해 보세요."
                else:
                    msg = msg + "이 인간은 [트롤]일 가능성이 높네요. 닷지를 하든 맞트롤을 하든 알아서 하시길!"

    return msg


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_troll_man(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)




import requests
import os

GOODS_CODE = "26005547"

PERF_URL = f"https://tickets.interpark.com/goods/{GOODS_CODE}"
BASE_URL = "https://api-ticketfront.interpark.com"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

PLAY_DATES = ["20260613"]

# 테스트용: "" / 실전: "SOUND CHECK"
TARGET_KEYWORD = ""

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://tickets.interpark.com/",
    "Origin": "https://tickets.interpark.com",
    "Accept": "application/json, text/plain, */*"}
def get_grade_map():
    url = f"{BASE_URL}/v1/goods/{GOODS_CODE}/bestprices/group"

    resp = requests.get(url, headers=HEADERS, timeout=10)
    print("등급조회:", resp.status_code)

    resp.raise_for_status()

    data = resp.json().get("data", [])

    result = {}
    for g in data:
        if g.get("seatGrade"):
            result[str(g["seatGrade"])] = g.get("seatGradeName", "?")

    return result

def check_remain(date, grade_map):
    url = f"{BASE_URL}/v1/goods/{GOODS_CODE}/playSeq/PlayDate/{date}/ALL"

    resp = requests.get(url, headers=HEADERS, timeout=10)
    print("잔여조회:", resp.status_code)

    resp.raise_for_status()

    seats = resp.json().get("data", {}).get("remainSeat", [])

    result = []

    for r in seats:
        grade = grade_map.get(
            str(r["seatGrade"]),
            r.get("seatGradeName", "?")
        )

        if TARGET_KEYWORD.lower() in grade.lower():
            msg = f"✅ {grade} - 잔여 {r['remainCnt']}석 ({r.get('playSeqName','')})"
            result.append(msg)

    return result

def main():
    try:
        print("체크 시작")

        grade_map = get_grade_map()

        available = []

        for date in PLAY_DATES:
            lines = check_remain(date, grade_map)

            if lines:
                fmt = f"{date[:4]}-{date[4:6]}-{date[6:]}"
                block = f"📅 {fmt}\n" + "\n".join(lines)
                available.append(block)

        if available:
            send_telegram(
                "🚨 인터파크 취소표 발생!\n\n"
                + "\n\n".join(available)
                + f"\n\n🔗 {PERF_URL}"
            )

        print("완료")

    except Exception as e:
        print("오류:", e)

if __name__ == "__main__": 
    main()
#trigger

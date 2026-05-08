
# monitor.py (인터파크)
import requests, os

GOODS_CODE = "26005547"
PERF_URL = f"https://tickets.interpark.com/goods/{GOODS_CODE}"
BASE_URL = "https://api-ticketfront.interpark.com"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# 모니터링 날짜
PLAY_DATES = ["20260613"]

# 찾고 싶은 좌석 등급
TARGET_KEYWORD = "SOUND CHECK"

HEADERS = {
    "sec-ch-ua-platform": '"macOS"',
    "referer": "https://tickets.interpark.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua": '"HeadlessChrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "accept-language": "ko-KR",
    "sec-ch-ua-mobile": "?0",
}

def get_grade_map():
    resp = requests.get(
        f"{BASE_URL}/v1/goods/{GOODS_CODE}/bestprices/group",
        headers=HEADERS,
        timeout=10
    )

    return {
        str(g["seatGrade"]): g.get("seatGradeName", "?")
        for g in resp.json().get("data", [])
        if g.get("seatGrade")
    }

def check_remain(date, grade_map):
    resp = requests.get(
        f"{BASE_URL}/v1/goods/{GOODS_CODE}/playSeq/PlayDate/{date}/ALL",
        headers=HEADERS,
        timeout=10
    )

    seats = resp.json().get("data", {}).get("remainSeat", [])

    result = []

    for r in seats:
        grade = grade_map.get(
            str(r["seatGrade"]),
            r.get("seatGradeName", "?")
        )

        # SOUND CHECK 좌석만 감지
        if TARGET_KEYWORD.lower() in grade.lower():
            result.append(
                f"✅ {grade} - 잔여: {r['remainCnt']}석 ({r.get('playSeqName','')})"
            )

    return result

def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )

def main():
    grade_map = get_grade_map()

    available = []

    for date in PLAY_DATES:
        lines = check_remain(date, grade_map)

        fmt = f"{date[:4]}년 {date[4:6]}월 {date[6:]}일"

        if lines:
            available.append(
                f"📅 {fmt}\n" + "\n".join(lines)
            )

    if available:
        send_telegram(
            "🚨 인터파크 SOUND CHECK 취소표 발생!\n\n"
            + "\n\n".join(available)
            + f"\n\n🔗 {PERF_URL}"
        )

if __name__ == "__main__":
    main()

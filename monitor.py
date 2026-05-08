for date in PLAY_DATES:
            lines = check_remain(date, grade_map)

            fmt = (
                f"{date[:4]}년 "
                f"{date[4:6]}월 "
                f"{date[6:]}일"
            )

            if lines:
                available.append(
                    f"📅 {fmt}\n"
                    + "\n".join(lines)
                )

        if available:
            send_telegram(
                "🚨 인터파크 SOUND CHECK 취소표 발생!\n\n"
                + "\n\n".join(available)
                + f"\n\n🔗 {PERF_URL}"
            )

        print("모니터링 완료")

    except Exception as e:
        print("오류:", str(e))
        print("모니터링 중단")

if __name__ == "__main__":
    main()

"""
Собирает количество моделей категории "пара" (Couple*), сейчас в эфире на
BongaCams, и дописывает строку в couples_online_log.csv.

Публичный affiliate API BongaCams, без авторизации. Никаких секретов и
никаких личных данных — только время (UTC) и агрегированное число.
Запускается по расписанию через .github/workflows/collect.yml.
"""

import csv
import json
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://bngprm.com/promo.php?c=802403&type=api&api_v=1&api_type=json&lang=en"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
LOG_PATH = Path(__file__).parent / "couples_online_log.csv"


def fetch_models():
    # Тот же сертификатный нюанс, что у остальных запросов к этому CDN
    # (см. соседний проект profile-prototype): Basic Constraints
    # промежуточного CA не помечен critical — браузеры это прощают,
    # Python ssl/OpenSSL 3.x нет. Публичный эндпоинт без секретов.
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(API_URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def main():
    models = fetch_models()
    couples_online = sum(1 for m in models if str(m.get("gender") or "").lower().startswith("couple"))
    total_online = len(models)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    is_new = not LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["ts_utc", "couples_online", "total_online"])
        writer.writerow([now, couples_online, total_online])

    print(f"{now}: {couples_online} couples online (of {total_online} total)")


if __name__ == "__main__":
    main()

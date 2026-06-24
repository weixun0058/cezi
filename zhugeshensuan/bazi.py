"""Command-line example for the deterministic bazi service."""

import json

from .bazi_service import calculate_bazi


def get_bazi(birth_date, birth_time, gender="男", timezone="Asia/Shanghai"):
    return calculate_bazi(
        {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "gender": gender,
            "timezone": timezone,
        }
    )


if __name__ == "__main__":
    example = get_bazi("1990-01-01", "12:30")
    print(json.dumps(example, ensure_ascii=False, indent=2))

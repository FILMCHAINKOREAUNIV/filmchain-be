import os
from typing import Dict, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def _get_client():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY 환경변수가 설정되어 있지 않습니다")
    return build("youtube", "v3", developerKey=api_key, cache_discovery=False)


def fetch_video_stats(video_ids: List[str]) -> Dict[str, Dict[str, Optional[object]]]:
    """
    최대 50개의 비디오 ID에 대해 조회수(statistics.viewCount)와 태그(snippet.tags)를 가져옴
    반환 형식: { 비디오ID: {"view_count": int, "hashtags": Optional[str]} }
    """
    result: Dict[str, Dict[str, Optional[object]]] = {}
    if not video_ids:
        return result

    client = _get_client()
    try:
        request = client.videos().list(
            part="statistics,snippet",
            id=",".join(video_ids),
            maxResults=50,
        )
        response = request.execute()

        for item in response.get("items", []):
            vid = item.get("id")
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            view_count_str = stats.get("viewCount", "0")
            try:
                view_count = int(view_count_str)
            except Exception:
                view_count = 0

            tags = snippet.get("tags") or []
            hashtags: Optional[str] = None
            if tags:
                normalized = []
                for t in tags:
                    t = (t or "").strip()
                    if not t:
                        continue
                    if not t.startswith("#"):
                        t = f"#{t}"
                    normalized.append(t)
                if normalized:
                    # 공백으로 구분된 하나의 문자열로 저장(예: "#tag1 #tag2")
                    hashtags = " ".join(normalized)

            if vid:
                result[vid] = {"view_count": view_count, "hashtags": hashtags}
    except HttpError as e:
        raise e

    return result

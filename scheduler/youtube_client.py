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
    최대 50개의 비디오 ID에 대해 조회수(statistics.viewCount), 제목(snippet.title), 태그(snippet.tags)를 가져옴
    반환 형식: { 비디오ID: {"view_count": int, "title": Optional[str], "hashtags": Optional[str]} }
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

            # 영상 제목 가져오기
            title = snippet.get("title") or ""
            description = snippet.get("description") or ""
            
            def extract_hashtags(text: str) -> List[str]:
                return [w for w in text.split() if w.startswith("#")]
            
            hashtags_set = set()
            meta_tags = snippet.get("tags") or []
            hashtags: Optional[str] = None

            if meta_tags:
                for t in meta_tags:
                    t = (t or "").strip()
                    if not t:
                        continue
                    if not t.startswith("#"):
                        t = f"#{t}"
                    hashtags_set.add(t)

            for w in extract_hashtags(title) + extract_hashtags(description):
                hashtags_set.add(w.strip())

            hashtags = " ".join(sorted(hashtags_set)) if hashtags_set else None

            if vid:
                result[vid] = {"view_count": view_count, "title": title, "hashtags": hashtags}
    except HttpError as e:
        raise e

    return result

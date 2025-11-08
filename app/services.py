from urllib.parse import urlparse, parse_qs
from fastapi import HTTPException, status

def parse_video_id(url: str) -> str:
    """
    주어진 유튜브 URL에서 video_id를 추출합니다.
    지원되는 URL 형식:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    """
    parsed_url = urlparse(url)
    
    # youtu.be 형태
    if parsed_url.hostname == 'youtu.be':
        video_id = parsed_url.path.lstrip('/')
        if video_id:
            return video_id
    
    if parsed_url.hostname in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
        # '/shorts/' 형태
        if parsed_url.path.startswith('/shorts/'):
            video_id = parsed_url.path.split('/')[2]
            if video_id:
                return video_id
        
        # 'watch' 경로 형태
        if parsed_url.path == '/watch':
            query_params = parse_qs(parsed_url.query)
            video_id_list = query_params.get('v')
            if video_id_list:
                return video_id_list[0]
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="유효한 유튜브 URL이 아닙니다."
    )
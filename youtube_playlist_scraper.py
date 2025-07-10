
import pandas as pd
from googleapiclient.discovery import build
from os import getenv
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

# Chave da API do YouTube carregada da variável de ambiente
API_KEY = getenv("YOUTUBE_API_KEY")  

# ID da playlist extraído da URL
PLAYLIST_ID = "PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj"

# Inicializa o cliente da API do YouTube
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_video_ids(playlist_id: str) -> List[str]:
    """Coletar os IDs dos vídeos de uma playlist do YouTube.

    Args:
        playlist_id: O ID da playlist do YouTube.

    Returns:
        Uma lista de IDs dos vídeos da playlist.

    Raises:
        googleapiclient.errors.HttpError: Se a requisição à API falhar.
    """
    video_ids: List[str] = []
    next_page_token: Optional[str] = None

    while True:
        # Busca itens da playlist com paginação
        res = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        # Extrai IDs dos vídeos da resposta
        for item in res["items"]:
            video_ids.append(item["contentDetails"]["videoId"])

        # Verifica se há próxima página
        next_page_token = res.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids

def get_video_details(video_ids: List[str]) -> List[Dict[str, any]]:
    """Coletar detalhes de uma lista de vídeos do YouTube.

    Args:
        video_ids: Lista de IDs dos vídeos para coletar detalhes.

    Returns:
        Uma lista de dicionários contendo detalhes dos vídeos (ID, título, descrição,
        data de publicação, curtidas, visualizações, comentários, URL da miniatura).

    Raises:
        googleapiclient.errors.HttpError: Se a requisição à API falhar.
    """
    videos_data: List[Dict[str, any]] = []

    # Processa IDs dos vídeos em lotes de 50
    for i in range(0, len(video_ids), 50):
        chunk: List[str] = video_ids[i:i+50]
        res = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(chunk)
        ).execute()

        # Extrai detalhes de cada vídeo
        for item in res["items"]:
            snippet = item["snippet"]
            stats = item["statistics"]

            video_info: Dict[str, any] = {
                "video_id": item["id"],
                "titulo": snippet.get("title"),
                "descricao": snippet.get("description"),
                "data_publicacao": snippet.get("publishedAt"),
                "likes": int(stats.get("likeCount", 0)),
                "views": int(stats.get("viewCount", 0)),
                "comentarios": int(stats.get("commentCount", 0)),
                "thumbnail_url": snippet["thumbnails"]["high"]["url"]
            }
            videos_data.append(video_info)

    return videos_data

if __name__ == "__main__":
    print("Coletando vídeos da playlist...")
    video_ids: List[str] = get_video_ids(PLAYLIST_ID)

    print(f"{len(video_ids)} vídeos encontrados. Coletando detalhes...")
    video_data: List[Dict[str, any]] = get_video_details(video_ids)

    print("Exportando para CSV...")
    df: pd.DataFrame = pd.DataFrame(video_data)
    df.to_csv("youtube_playlist_data.csv", index=False, encoding="utf-8-sig")

    print("Concluído! Arquivo salvo como 'youtube_playlist_data.csv'")

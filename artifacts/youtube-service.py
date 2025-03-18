import os
import logging
import tempfile
import re
import time
from datetime import datetime
from urllib.parse import parse_qs, urlparse

# Third-party imports
import yt_dlp
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.discovery import build

# Application imports
from drumtrackkit.config import Config
from drumtrackkit.utils.exceptions import ResourceNotFoundError, ServiceUnavailableError

# Set up logging
logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for interacting with YouTube API and downloading videos"""

    def __init__(self):
        """Initialize the YouTube service with API key"""
        self.api_key = Config.YOUTUBE_API_KEY
        self.download_dir = Config.AUDIO_DOWNLOAD_DIR
        self.youtube_api = None

        # Create download directory if it doesn't exist
        os.makedirs(self.download_dir, exist_ok=True)

    def _get_youtube_api(self):
        """Get or create YouTube API client"""
        if self.youtube_api is None:
            try:
                self.youtube_api = build('youtube', 'v3', developerKey=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize YouTube API: {str(e)}", exc_info=True)
                raise ServiceUnavailableError("YouTube API is currently unavailable")
        return self.youtube_api

    def _extract_video_id(self, url):
        """Extract YouTube video ID from URL"""
        # Handle youtu.be format
        if 'youtu.be' in url:
            return url.split('/')[-1].split('?')[0]

        # Handle youtube.com format
        parsed_url = urlparse(url)
        if parsed_url.netloc == 'www.youtube.com' or parsed_url.netloc == 'youtube.com':
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
            elif parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[-1]
            elif parsed_url.path.startswith('/v/'):
                return parsed_url.path.split('/')[-1]

        # If we can't extract a video ID, raise an error
        raise ValueError(f"Could not extract video ID from URL: {url}")

    def search_videos(self, query, max_results=20):
        """
        Search YouTube for videos matching the query

        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return

        Returns:
            list: List of video information dictionaries
        """
        try:
            youtube = self._get_youtube_api()

            # Add drum-related terms if not already in query
            if not any(term in query.lower() for term in ['drum', 'drummer', 'drumming', 'percussion']):
                query = f"{query} drums"

            # Execute search
            search_response = youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                videoEmbeddable='true',
                videoSyndicated='true'
            ).execute()

            # Create list of video IDs to get durations
            video_ids = [item['id']['videoId'] for item in search_response['items']]

            # Get video details (including duration)
            if video_ids:
                video_response = youtube.videos().list(
                    part='contentDetails,statistics',
                    id=','.join(video_ids)
                ).execute()

                # Create a map of video ID to duration
                duration_map = {}
                for item in video_response['items']:
                    duration = item['contentDetails']['duration']
                    # Convert ISO 8601 duration to seconds
                    seconds = self._iso8601_to_seconds(duration)
                    duration_map[item['id']] = seconds
            else:
                duration_map = {}

            # Format results
            results = []
            for item in search_response['items']:
                video_id = item['id']['videoId']
                snippet = item['snippet']

                results.append({
                    'id': video_id,
                    'title': snippet['title'],
                    'thumbnail': snippet['thumbnails']['high']['url'],
                    'channel': snippet['channelTitle'],
                    'duration': duration_map.get(video_id, 0)
                })

            return results

        except googleapiclient.errors.HttpError as e:
            logger.error(f"YouTube API error: {str(e)}", exc_info=True)
            if e.resp.status == 403:
                raise ServiceUnavailableError("YouTube API quota exceeded")
            raise ServiceUnavailableError(f"YouTube API error: {str(e)}")

        except Exception as e:
            logger.error(f"Error searching YouTube: {str(e)}", exc_info=True)
            raise ServiceUnavailableError(f"Error searching YouTube: {str(e)}")

    def _iso8601_to_seconds(self, duration):
        """
        Convert ISO 8601 duration format to seconds
        Example: PT1H30M15S -> 5415 seconds
        """
        hours = re.search(r'(\d+)H', duration)
        minutes = re.search(r'(\d+)M', duration)
        seconds = re.search(r'(\d+)S', duration)

        hours = int(hours.group(1)) if hours else 0
        minutes = int(minutes.group(1)) if minutes else 0
        seconds = int(seconds.group(1)) if seconds else 0

        return hours * 3600 + minutes * 60 + seconds

    def download_audio(self, video_url, start_time=0, duration=180):
        """
        Download audio from a YouTube video

        Args:
            video_url (str): YouTube video URL
            start_time (int): Start time in seconds
            duration (int): Duration to download in seconds

        Returns:
            str: Path to downloaded audio file
        """
        try:
            # Extract video ID
            video_id = self._extract_video_id(video_url)

            # Create output filename with timestamp to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{video_id}_{timestamp}_{start_time}_{duration}.wav"
            output_path = os.path.join(self.download_dir, output_filename)

            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(self.download_dir, f"{video_id}_{timestamp}_full"),
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True
            }

            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                downloaded_file = ydl.prepare_filename(info)

            # Downloaded file will have .wav extension due to postprocessor
            downloaded_file = os.path.splitext(downloaded_file)[0] + '.wav'

            # If we need to trim the audio, do it with FFmpeg
            if start_time > 0 or duration < 600:  # Only trim if needed
                import subprocess
                temp_file = downloaded_file

                # Construct FFmpeg command
                cmd = [
                    'ffmpeg',
                    '-i', temp_file,
                    '-ss', str(start_time),
                    '-t', str(duration),
                    '-y',  # Overwrite output file if it exists
                    output_path
                ]

                # Execute FFmpeg
                result = subprocess.run(cmd, capture_output=True, text=True)

                # Check if FFmpeg was successful
                if result.returncode != 0:
                    logger.error(f"FFmpeg error: {result.stderr}")
                    raise RuntimeError(f"Failed to trim audio: {result.stderr}")

                # Remove the original full file
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {temp_file}: {str(e)}")
            else:
                # Just rename the file if no trimming is needed
                os.rename(downloaded_file, output_path)

            return output_path

        except yt_dlp.utils.DownloadError as e:
            logger.error(f"YouTube download error: {str(e)}", exc_info=True)
            if 'This video is unavailable' in str(e):
                raise ResourceNotFoundError("Video not found or not available")
            raise ServiceUnavailableError(f"Failed to download YouTube video: {str(e)}")

        except Exception as e:
            logger.error(f"Error downloading YouTube video: {str(e)}", exc_info=True)
            raise ServiceUnavailableError(f"Error downloading YouTube video: {str(e)}")

    def get_video_info(self, video_url):
        """
        Get information about a YouTube video

        Args:
            video_url (str): YouTube video URL

        Returns:
            dict: Video information
        """
        try:
            # Extract video ID
            video_id = self._extract_video_id(video_url)

            # Get video details from API
            youtube = self._get_youtube_api()
            video_response = youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()

            # Check if video exists
            if not video_response['items']:
                raise ResourceNotFoundError(f"Video not found: {video_id}")

            video = video_response['items'][0]
            snippet = video['snippet']
            content_details = video['contentDetails']
            statistics = video['statistics']

            # Format duration
            duration_seconds = self._iso8601_to_seconds(content_details['duration'])

            return {
                'id': video_id,
                'title': snippet['title'],
                'channel': snippet['channelTitle'],
                'description': snippet['description'],
                'thumbnail': snippet['thumbnails']['high']['url'],
                'duration': duration_seconds,
                'published_at': snippet['publishedAt'],
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0))
            }

        except googleapiclient.errors.HttpError as e:
            logger.error(f"YouTube API error: {str(e)}", exc_info=True)
            if e.resp.status == 404:
                raise ResourceNotFoundError("Video not found")
            raise ServiceUnavailableError(f"YouTube API error: {str(e)}")

        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}", exc_info=True)
            raise ServiceUnavailableError(f"Error getting video info: {str(e)}")
import random
import time
import sys

from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from .constants import MAX_RETRIES, RETRIABLE_EXCEPTIONS, RETRIABLE_STATUS_CODES
from .presets import PresetOptions


def initialize_upload(youtube: Resource, options: PresetOptions):
    body_status = {"selfDeclaredMadeForKids": False}
    if options.publish_at == "Now":
        body_status["privacyStatus"] = "public"
    else:
        body_status["privacyStatus"] = "private"
        body_status["publishAt"] = options.publish_at.isoformat()

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=options.tags,
            categoryId=options.category_id,
        ),
        status=body_status,
    )

    print("Uploading video...")
    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(
            options.file, chunksize=256 * 1024 * 100, resumable=True
        ),
    )
    video_id = resumable_upload(insert_request)

    print(f"Upload Complete: [videoId={video_id}]")

    if options.playlist_id:
        print("Adding to playlist...")
        youtube.playlistItems().insert(
            part="snippet",
            body=dict(
                snippet=dict(
                    playlistId=options.playlist_id,
                    resourceId=dict(kind="youtube#video", videoId=video_id),
                )
            ),
        ).execute()
        print("Added to playlist")

    if options.thumbnail_path:
        print("Uploading thumbnail...")
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=options.thumbnail_path,
        ).execute()
        print("Thumbnail uploaded")


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0

    def print_progress(progress):
        bar_size = 20
        completed = "█" * int(bar_size * progress)
        remaining = "░" * (bar_size - len(completed))
        sys.stdout.write(f"\r{completed}{remaining} {int(progress * 100)}%")
        sys.stdout.flush()

    print_progress(0)

    while response is None:
        try:
            status, response = insert_request.next_chunk()

            progress = (
                1 if response is not None else status.progress() if status else None
            )
            if progress is not None:
                print_progress(progress)

            if response is not None:
                print()
                if "id" in response:
                    print("File '%s' was successfully uploaded." % response["id"])
                    return response["id"]
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (
                    e.resp.status,
                    e.content,
                )
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2**retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)

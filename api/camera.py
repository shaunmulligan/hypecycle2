import os, glob, asyncio
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

picam2 = Picamera2()
video_config = picam2.create_video_configuration()
still_config = picam2.create_still_configuration()

router = APIRouter()
loop = asyncio.get_running_loop()

@router.get("/videos/", response_model=List[str])
async def get_list_of_videos():
    videos = os.listdir('data/videos')
    videos.remove('info.txt')
    return videos

@router.get("/videos/{filename}")
async def download_a_video(filename: str):
    videos = os.listdir('data/videos')
    if (filename in videos):
        return FileResponse("data/videos/"+filename)
    else:
        raise HTTPException(status_code=404, detail="video not found")

@router.delete("/videos/")
async def delete_all_videos():
    files = glob.glob('data/videos/*.mp4', recursive=True)
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))
            raise HTTPException(status_code=404, detail="video not found")
    return "OK"

@router.get("/images/", response_model=List[str])
async def get_list_of_images():
    images = os.listdir('data/images')
    images.remove('info.txt')
    return images

@router.get("/images/{filename}")
async def download_an_image(filename: str):
    images = os.listdir('data/images')
    if (filename in images):
        return FileResponse("data/images/"+filename)
    else:
        raise HTTPException(status_code=404, detail="image not found")

@router.delete("/images")
async def delete_all_images():
    files = glob.glob('data/images/*.jpg', recursive=True)
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))
            raise HTTPException(status_code=404, detail="image not found")
    return "OK"

@router.post("/record")
async def start_video_recording():
    global picam2
    encoder = H264Encoder(10000000)
    picam2.configure(video_config)
    filename = "data/videos/" + datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + ".mp4"
    output = FfmpegOutput(filename)
    picam2.start_recording(encoder, output)
    return filename

@router.post("/stop")
async def stop_video_recording():
    global picam2
    picam2.stop_recording()
    return "OK"

@router.get("/snap")
async def take_a_photo():
    global picam2
    picam2.start()
    filename = "data/images/" + datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + ".jpg"
    metadata = await loop.run_in_executor(None, picam2.capture_file, filename)
    picam2.stop()
    while True:
        if not os.path.exists(filename):
            print("{} not found yet.".format(filename))
            asyncio.sleep(interval)
        else:
            print("{} found!".format(filename))
            return FileResponse(filename)
            break
    
import copy
import json
import logging
import re
import time
import traceback

from celery import shared_task, current_task
from eventlet.green.profile import thread
from eventlet.hubs import threading

from apps.kohya_ss.models import AsyncTask

logger = logging.getLogger('log_error')

from gradio_client import Client
from kohya_ss_admin.settings import *


def wait_max_1_hour(client):
    i = 0
    while client.predict(api_name="/is_train_lora"):
        time.sleep(10)
        i += 1
        if i > 360:
            return

def for_n_run(client, num):
    for i in range(num):
        client.predict(api_name="/is_train_lora")
        time.sleep(5)

import requests
import os
from PIL import Image

def download_image(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"img save: {save_path}")
    except Exception as e:
        print(f"download img failed: {url}, Exception: {e}")

def crop_image(image_path, output_path, target_width, target_height):
    try:
        target_width = int(target_width)
        target_height = int(target_height)
        image = Image.open(image_path)
        original_width, original_height = image.size

        original_ratio = original_width / original_height
        target_ratio = target_width / target_height

        if original_ratio > target_ratio:
            new_height = target_height
            new_width = int(original_width * (new_height / original_height))
        else:
            new_width = target_width
            new_height = int(original_height * (new_width / original_width))

        resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)

        left = (new_width - target_width) / 2
        top = (new_height - target_height) / 2
        right = left + target_width
        bottom = top + target_height

        left = max(0, left)
        top = max(0, top)
        right = min(new_width, right)
        bottom = min(new_height, bottom)

        cropped_image = resized_image.crop((left, top, right, bottom))

        cropped_image.save(output_path)
        print(f"img crop save: {output_path}")
    except Exception as e:
        print(f"crop failed: {image_path}, Exception: {e}")

def download_and_crop_images(img_urls, save_dir, crop_dir, target_width, target_height):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for i, url in enumerate(img_urls):
        try:
            file_name = f"image_{i + 1}.png"
            download_path = os.path.join(save_dir, file_name)
            crop_path = os.path.join(crop_dir, f"cropped_{file_name}")

            download_image(url, download_path)

            crop_image(download_path, crop_path, target_width, target_height)
        except Exception as e:
            print(traceback.format_exc())
            pass

def check_model_files(lora_path, model_name):
    model_dir = os.path.join(lora_path, "model")
    for i in ["safetensors", "ckpt"]:
        safetensors_path = os.path.join(model_dir, f"{model_name}.{i}")
        if os.path.exists(safetensors_path):
            return safetensors_path

        pattern = re.compile(rf"{model_name}.*{i}")
        for file in os.listdir(model_dir):
            if pattern.match(file):
                return os.path.join(model_dir, file)
    return None

@shared_task
def kohya_ss(kwargs, pop_params):

    task_id = current_task.request.id
    try:
        kwargs["api_name"] = "/lora_train_api"
        kwargs["celery_task_id"] = task_id

        logger.info(f"task_id: {task_id}, kwargs:{kwargs}, pop_params:{pop_params}")
        lora_path = pop_params["lora_path"]
        lora_name = pop_params["lora_name"]
        imgs = pop_params["imgs"]
        per_pic_learn_count = pop_params["per_pic_learn_count"]
        crop_width_height = pop_params["crop_width_height"]
        is_tag = pop_params.get('is_tag', True)

        download_and_crop_images(imgs, os.path.join(lora_path, 'ori_img', f"{per_pic_learn_count}_{lora_name}"), os.path.join(lora_path, 'img', f"{per_pic_learn_count}_{lora_name}"),*crop_width_height)

        client = Client(KOHYA_SS_CONF["url"])

        wait_max_1_hour(client)

        import  threading
        threading.Thread(target=for_n_run, args=(client, 4)).start()

        with open(rf"{KOHYA_SS_CONF['dirname']}/training.txt", "w") as file:
            file.write(json.dumps({"task_id": task_id, "status":"TAGING",  "msg":""}))
        task = AsyncTask.objects.get(task_id=task_id)
        task.status = 'TAGING'
        task.save()

        if is_tag:
            blip_captions_ret = client.predict(
                train_data_dir=os.path.join(lora_path, 'img', f"{per_pic_learn_count}_{lora_name}"),
                caption_file_ext=".txt",
                batch_size=1,
                num_beams=1,
                top_p=0.9,
                max_length=100,
                min_length=5,
                beam_search=True,
                prefix=f"{lora_name},",
                postfix="",
                api_name="/blip_captions_api"
            )
            logger.info(f"blip_captions_ret: {blip_captions_ret}")
            blip_captions_ret = json.loads(blip_captions_ret)

            if blip_captions_ret["code"] != 20000:
                status = "FAILED"
                task = AsyncTask.objects.get(task_id=task_id)
                task.status = status
                task.ret = json.dumps(
                    {"status": status, "msg": f"tag failed{blip_captions_ret}", "task_id": task_id})
                task.save()
                return


        result = client.predict(**kwargs)
        with open(rf"{KOHYA_SS_CONF['dirname']}/training.txt", "w") as file:
            file.write(json.dumps({"task_id": task_id, "status": "TRAINING", "msg": ""}))
        logger.info(f"result:{result}")

        task = AsyncTask.objects.get(task_id=task_id)
        task.status = 'TRAINING'
        task.save()

        time.sleep(10)
        wait_max_1_hour(client)

        with open(rf"{KOHYA_SS_CONF['dirname']}/training.txt", "r") as file:
            ret = json.load(file)

        if ret.get("task_id", "") != task_id:
            if check_model_files(lora_path, lora_name):
                status = "SUCCESS"
                task = AsyncTask.objects.get(task_id=task_id)
                task.status = status
                task.ret = json.dumps({"status":status, "msg":f"", "task_id":task_id})
                task.save()
            else:
                status = "FAILED"
                task = AsyncTask.objects.get(task_id=task_id)
                task.status = status
                task.ret = json.dumps({"status":status,"msg":f"tain over，but in {lora_path} not found {lora_name} prefix lora model", "task_id":task_id})
                task.save()
        else:
            if not check_model_files(lora_path, lora_name):
                status = "FAILED"
                task = AsyncTask.objects.get(task_id=task_id)
                task.status = status
                task.ret = json.dumps({"status":status,"msg":f"tain over，but in {lora_path} not found {lora_name} prefix lora model", "task_id":task_id})
                task.save()
            else:
                task = AsyncTask.objects.get(task_id=task_id)
                task.status = ret["status"]
                task.ret = json.dumps(ret)
                task.save()

    except Exception as e:
        logger.error(traceback.format_exc())
        task = AsyncTask.objects.get(task_id=task_id)
        task.status = 'FAILED'
        task.ret =  json.dumps({"task_id": task_id, "status":'celery failed',  "msg":f"{traceback.format_exc()}"})
        task.save()
        return str(e)
    return []


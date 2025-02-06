import json
import logging
import random
import re
import shutil
import traceback

from rest_framework import views
from rest_framework.response import Response

# from apps.api_auth.authorizations import JWTAuthentication
# from lib.Utils import Utils
# from rest_framework.permissions import IsAuthenticated
import os
from django.conf import settings

import lib.KohyaSsArgs as KohyaArgs

from kohya_ss_admin.tasks import kohya_ss

from apps.kohya_ss.models import AsyncTask
from gradio_client import Client

pwd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger('log_error')

from rest_framework import serializers

class AsyncTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsyncTask
        fields = '__all__'

class CancelTrain(views.APIView):
    def post(self, request):
        try:
            from gradio_client import Client
            client = Client(settings.KOHYA_SS_CONF["url"])
            ret = client.predict(api_name="/is_train_lora")
            if not ret:
                ret = client.predict(api_name="/kill_command_1")
                return Response(data={"data": ret, "code": 20000, "message": "There are no training tasks being done. Idle"})
            ret = client.predict(api_name="/kill_command_1")
            tasks = AsyncTask.objects.filter(status__in=["TRAINING", "TAGING"])
            tasks.update(status="CANCEL")
            return Response(data={"data": ret, "code": 20000, "message": "CancelTrain success"})
        except Exception as e:
            logger.error(str(traceback.format_exc()))
            return Response(data={"data": -1, "code": 20002, "message": f"CancelTrain Exception:{e}"})

class IsTraining(views.APIView):
    def get(self, request):
        try:
            client = Client(settings.KOHYA_SS_CONF["url"])
            ret = client.predict(api_name="/is_train_lora")
            return Response(data={"data": ret, "code": 20000, "message": "query lora is training success"})
        except Exception as e:
            logger.error(str(traceback.format_exc()))
            return Response(data={"data": -1, "code": 20002, "message": f"query lora is training Exception:{e}"})

class Qsize(views.APIView):
    def get(self, request):
        try:
            pending_task_count = AsyncTask.objects.filter(status="pending").count()
            return Response(data={"data": pending_task_count, "code": 20000, "message": "query queue size success"})
        except Exception as e:
            logger.error(str(traceback.format_exc()))
            return Response(data={"data": -1, "code": 20002, "message": f"query queue size Exception:{e}"})


class TrainTask(views.APIView):
    def get(self, request):
        try:
            key = 'task_id'
            task_id = request.GET.get(f'{key}', '')
            if not task_id:
                return Response(data={"data": [], "code": 20001, "message": f"query train task failed:need {key}"})

            try:
                async_task = AsyncTask.objects.filter(task_id=task_id).first()
                if not async_task:
                    return Response(data={"data": [], "code": 20001, "message": f"query train task failed:{task_id} does not exists"})

                serializer = AsyncTaskSerializer(async_task)
                async_task_data = serializer.data
            except Exception as e:
                return Response(data={"data": [], "code": 20001, "message": f"query train task failed:{task_id} does not exists. {e}"})
            return Response(data={"data": async_task_data, "code": 20000, "message": "query train task success"})
        except Exception as e:
            logger.error(str(traceback.format_exc()))
            return Response(data={"data": [], "code": 20002, "message": f"query train task Exception:{e}"})

    def post(self, request):

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

        proc_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        proc_dir = os.path.join(os.path.dirname(proc_dir), 'train_res')
        try:
            ori_data = request.body
            if not ori_data:
                return Response(data={"data": {}, "code": 20001, "message": "params must not be empty"})
            ori_data = json.loads(ori_data)
            task_params = dict(ori_data)
            imgs = ori_data.pop("imgs", [])
            is_tag = ori_data.pop("is_tag", True)
            if not imgs:
                raise Exception(f"imgs cannot be empty")

            if not isinstance(imgs, list):
                raise Exception(f"imgs must be a list")


            lora_name = ori_data.pop("lora_name", "")
            if not lora_name:
                raise Exception(f"lora_name cannot be empty")
            pretrained_model_name_or_path = ori_data.get("base_model", "")
            # logging_dir = ori_data.get("logging_dir", "")
            # train_data_dir = ori_data.get("train_data_dir", "")
            # output_dir = ori_data.get("output_dir", "")
            # reg_data_dir = ori_data.get("reg_data_dir", "")
            for i in ['logging_dir', 'train_data_dir', "reg_data_dir"]:
                data_dir = ori_data.get(i, "")
                if data_dir and not os.path.exists(data_dir):
                    raise Exception(f"{i}:{data_dir} does not exist.")


            lora_path = os.path.join(proc_dir, f"lora_of_{lora_name}")
            task_id_lora_dir = os.path.join(proc_dir, f"task_id_lora")
            if not os.path.exists(task_id_lora_dir):
                os.makedirs(task_id_lora_dir, exist_ok=True)

            per_pic_learn_count = ori_data.pop("per_pic_learn_count", 10)

            for i in ["log", 'img', 'reg', 'res', "sample", "model", f"img/{per_pic_learn_count}_{lora_name}"]:
                tdir = os.path.join(lora_path, i)
                if i == "img":
                    if os.path.exists(tdir):
                        shutil.rmtree(tdir)
                        os.makedirs(tdir)
                if not os.path.exists(tdir):
                    os.makedirs(tdir)

            if check_model_files(lora_path, lora_name):
                raise Exception(f"{check_model_files(lora_path, lora_name)} already exists.")


            if not pretrained_model_name_or_path or not os.path.exists(pretrained_model_name_or_path):
                raise Exception(f"base_model:{pretrained_model_name_or_path} does not exist.")

            ori_data["pretrained_model_name_or_path"] = pretrained_model_name_or_path
            if "logging_dir" not in ori_data:
                ori_data["logging_dir"] = os.path.join(lora_path, "log")
            if "train_data_dir" not in ori_data:
                ori_data["train_data_dir"] = os.path.join(lora_path, "img")
            # if "output_dir" not in ori_data:
            ori_data["output_dir"] = os.path.join(lora_path, "model")
            if not ori_data.get("output_name"):
                ori_data["output_name"] = lora_name


            """
            'max_resolution': '512,512',
            'network_dim': 8
            'network_alpha': 1,
            'train_batch_size': 1,
            "max_train_steps": 0, 
            "max_train_epochs":0,
            'epoch': 2,
            'save_every_n_epochs': 1,
            'learning_rate': 0.0001
            'text_encoder_lr': 0.0001,
            'unet_lr': 0.0001,
            """
            if 'max_resolution' in ori_data:
                if len(ori_data['max_resolution'].split(",")) != 2:
                    raise Exception(f"max_resolution:{ori_data['max_resolution']} type err. eg: '512,512'")

            train_params = dict(KohyaArgs.params)
            for k, v in train_params.items():
                type_v = type(v)
                if k in ori_data:
                    if type_v in [float, int]:
                        if not isinstance(ori_data[k], (float, int)):
                            raise Exception(f"{k} type error. need:{type_v} eg:{k, v}")
                    else:
                        if type_v == bool:
                            if not isinstance(ori_data[k], (bool)):
                                raise Exception(f"{k} type error. need:{type_v} eg:{k, v}")
                        else:
                            if type_v == str:
                                if not isinstance(ori_data[k], (str)):
                                    raise Exception(f"{k} type error. need:{type_v} eg:{k, v}")

                    train_params[k] = ori_data[k]

            r = kohya_ss.apply_async(
                args=[train_params,{
                    "imgs": imgs,
                    "lora_name": lora_name,
                    "lora_path": lora_path,
                    "per_pic_learn_count": per_pic_learn_count,
                    "is_tag": is_tag,
                    "crop_width_height": ori_data['max_resolution'].split(","),
                }])

            async_task = AsyncTask.objects.create(
                task_id=r.task_id,
                task_params=json.dumps(task_params),
            )
            async_task.save()

            with open(rf"{task_id_lora_dir}/{r.task_id}", "w") as file:
                file.write(f"{lora_path}|{lora_name}")

            return Response(data={"data": {"task_id": r.task_id}, "code": 20000, "message": f"tarin task created successfully" })

        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(data={"data": {}, "code": 20002, "message": "tarin task created Exception:" + str(e)})



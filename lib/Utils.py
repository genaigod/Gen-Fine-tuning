import collections
import hashlib
import json
import os
import base64
import time
from datetime import datetime
from io import BytesIO

from kohya_ss_admin.base import MEDIA_ROOT
from PIL import Image, PngImagePlugin

print('Utils...', MEDIA_ROOT)

class Utils:

    checkpoints = None
    checkpoints_ts = 0
    loras = None
    loras_ts = 0


    @classmethod
    def fix_base64_padding(cls, base64_string):
        missing_padding = len(base64_string) % 4
        if missing_padding != 0:
            base64_string += '=' * (4 - missing_padding)
        return base64_string

    @classmethod
    def get_file_dir(cls, username,  task_id=''):
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H-%M-%S-%f")

        user_directory = os.path.join(MEDIA_ROOT, username)
        date_directory = os.path.join(user_directory, date)
        if task_id:
            date_directory = os.path.join(date_directory, task_id)
        os.makedirs(date_directory, exist_ok=True)
        return date_directory

    @classmethod
    def _save_img_and_info(cls, image, file_name, save_meta=False):
        metadata = None
        tmp_v = {}
        for key, value in image.info.items():
            if isinstance(key, str) and isinstance(value, str):
                if metadata is None:
                    metadata = PngImagePlugin.PngInfo()
                metadata.add_text(key, value)
                tmp_v[key] = value
        print(f"{48, '_save_img_and_info', file_name, tmp_v}")

        if save_meta:
            image.save(file_name, format="PNG", pnginfo=metadata)
        else:
            image.save(file_name, format="PNG", pnginfo=None)


    @classmethod
    def get_url_file_name(cls,url):
        import os
        from urllib.parse import urlparse

        parsed_url = urlparse(url)
        path = parsed_url.path
        filename = os.path.basename(path)
        return filename


    @classmethod
    def save_image(cls, username, base64_data=None, img=None,  g_img_name='', task_id='', ai_info=True, final_name=None, save_meta=False):
        now = datetime.now()
        date = now.strftime("%Y_%m_%d")
        xtime = now.strftime("%H-%M-%S-%f")

        date_directory = cls.get_file_dir(username, task_id)

        if not final_name:
            filne_name = f"{xtime}.png" if not g_img_name else g_img_name
            if task_id:
                filne_name = f"{task_id}_{filne_name}"

            filne_name = f"{date}_{xtime.replace('-', '_')}_{filne_name}"
        else:
            filne_name = final_name

        file_path = os.path.join(date_directory, filne_name)
        print(25, file_path)

        if base64_data:
            print(34, base64_data[:40])

            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))

            print(f"88, {image.mode}")
            # if image.mode in ["P", "1", "L", "I"]:
            if image.mode in ["RGB"]:
                image = image.convert('RGB')

            if ai_info:
                cls._save_img_and_info(image, file_path, save_meta=save_meta)
            else:
                image.save(file_path,format="PNG", pnginfo=None)
        if img:
            print(f"88, {img.mode}")
            # if img.mode in ["P", "1", "L", "I"]:
            if img.mode in ["RGB"]:
                img = img.convert('RGB')

            if ai_info:
                cls._save_img_and_info(img, file_path, save_meta=save_meta)
            else:
                img.save(file_path,format="PNG", pnginfo=None) # 图片对象存储

        return filne_name, file_path

    @classmethod
    def get_checkpoints(cls, api, process=True, ck=None, redis_cli=None):
        for i in range(6):
            api.refresh_checkpoints()
            checkpoints = api.get_sd_models()

            # {'error': 'RuntimeError', 'detail': '', 'body': '', 'errors': 'dictionary changed size during iteration'}
            if not process:
                return checkpoints
            if "error" in checkpoints:
                time.sleep(1.2)
                continue
            ret = collections.defaultdict(list)
            for item in checkpoints:
                # type = item["filename"].split(os.path.sep)[-2]
                # title = item["title"]
                model_name = item["model_name"]
                title = item["title"]
                if ck:
                    if (ck in [model_name, title] or ck == item.get('hash', '')):
                        return item["title"]
                # ret[type].append({'title': title, 'name': model_name})
                ret[model_name].append({'title': model_name, 'name': model_name})
            if ck:
                return ''
            return ret
        raise Exception("get checkpoint failed")

    @classmethod
    def get_checkpoints_from_views(cls, api, process=True, ck=None, redis_cli=None):
        for i in range(6):
            data = redis_cli.get('checkpoints_all_key')
            checkpoints = []
            if data:
                checkpoints = json.loads(data)

            # {'error': 'RuntimeError', 'detail': '', 'body': '', 'errors': 'dictionary changed size during iteration'}
            if not process:
                return checkpoints
            if "error" in checkpoints:
                time.sleep(1.2)
                continue
            ret = collections.defaultdict(list)
            for item in checkpoints:
                # type = item["filename"].split(os.path.sep)[-2]
                # title = item["title"]
                model_name = item["model_name"]
                title = item["title"]
                if ck:
                    if (ck in [model_name, title] or ck == item.get('hash', '')):
                        return item["title"]
                # ret[type].append({'title': title, 'name': model_name})
                ret[model_name].append({'title': model_name, 'name': model_name})
            if ck:
                return ''
            return ret
        raise Exception("get checkpoint failed")

    @classmethod
    def get_checkpoint_by_hash(cls, api, hashStr, redis_cli, redis_key):
        data = redis_cli.get('checkpoints_all_key')
        checkpoints = []
        print(185, data)
        if data:
            checkpoints = json.loads(data)
        print(187, checkpoints)
        new_checkpoints = []
        hashStr = str(hashStr).lower()
        findFlag = False
        for item in checkpoints:
            if item.get('hash') and item.get('hash') == hashStr:
                new_checkpoints.append(item)
                findFlag = True
        if not findFlag:
            if redis_cli.exists(redis_key):
                value_bytes = redis_cli.hget(redis_key, hashStr)
                if value_bytes is not None:
                    ckval = value_bytes.decode('utf-8')  # 将字节串解码为字符串
                    for item in checkpoints:
                        if item["filename"] == ckval:
                            item["hash"] = hashStr
                            new_checkpoints.append(item)
        return new_checkpoints

    @classmethod
    def get_lora_by_hash(cls, api, hashStr, redis_cli, redis_key):
        data = redis_cli.get('loras_all_key')
        loras = []
        print(211, data)
        if data:
            loras = json.loads(data)
        print(211, loras)
        new_loras = []
        hashStr = str(hashStr).lower()
        if redis_cli.exists(redis_key):
            value_bytes = redis_cli.hget(redis_key, hashStr)
            if value_bytes is not None:
                loraval = value_bytes.decode('utf-8')  # 将字节串解码为字符串
                for item in loras:
                    if r"{}".format(item["path"]) == loraval:
                        item["hash"] = hashStr
                        new_loras.append(item)
        return new_loras

    @classmethod
    def get_loras(cls, api, process=True, lora=None, ):
        response = api.session.post(url=f"{api.baseurl}/refresh-loras")
        loras = api.get_loras()
        ret = collections.defaultdict(list)
        if not process:
            r = []
            for item in loras:
                if "metadata" in item:
                    del item["metadata"]
                r.append(item)
            return r
        for item in loras:
            # type = item["path"].split(os.path.sep)[-2]
            lora_name = item["name"]
            alias = item["alias"]
            if lora:
                if (lora in [lora_name, alias] or lora == item.get('hash', '')):
                    return item["name"]
            ret[lora_name].append({'name': item["name"]})
        if lora:
            return ''
        return ret

    @classmethod
    def get_loras_from_views(cls, api, redis_cli, process=True, lora=None, ):
        data = redis_cli.get('loras_all_key')
        loras = []
        if data:
            loras = json.loads(data)
        ret = collections.defaultdict(list)
        if not process:
            r = []
            for item in loras:
                if "metadata" in item:
                    del item["metadata"]
                r.append(item)
            return r
        for item in loras:
            # type = item["path"].split(os.path.sep)[-2]
            lora_name = item["name"]
            alias = item["alias"]
            if lora:
                if (lora in [lora_name, alias] or lora == item.get('hash', '')):
                    return item["name"]
            ret[lora_name].append({'name': item["name"]})
        if lora:
            return ''
        return ret
    @classmethod
    def get_process_form_val(cls, value):

        if value.startswith('-'):
            if value[1:].isdigit():
                return 0 - int(value[1:])
            if cls.is_float(value[1:]):
                return 0 - float(value[1:])

        # 判断是否是整数
        if value.isdigit():
            processed_value = int(value)
        # 判断是否是浮点数
        elif cls.is_float(value):
            processed_value = float(value)
        # 判断是否是布尔值
        elif value.lower() in ['true', 'false']:
            processed_value = value.lower() == 'true'
        # 默认为字符串类型
        else:
            try:
                processed_value = json.loads(value)
            except:
                processed_value = value
        return processed_value

    @classmethod
    # 判断浮点数
    def is_float(cls, value):
        try:
            float(value)
            return True
        except ValueError:
            return False


    @classmethod
    def get_signature(cls, username, secret):
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        print(date)
        sig_str = "%s%s" % (date, secret)
        new_secret = hashlib.md5(sig_str.encode('utf-8')).hexdigest()
        print(new_secret)
        sig_str = "%s%s" % (username, new_secret)
        sig = hashlib.md5(sig_str.encode('utf-8')).hexdigest()
        return sig

    @classmethod
    def auto_v2(cls, filename, sha256=False): #autov2
        hash_sha256 = hashlib.sha256()
        blksize = 1024 * 1024

        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(blksize), b""):
                hash_sha256.update(chunk)
        ha = hash_sha256.hexdigest() if sha256 else hash_sha256.hexdigest()[:10]
        ha = str(ha).lower()
        return ha


if __name__ == '__main__':

    print(Utils.get_signature('xx@23234@##', "714b9c04e3d8a1fc65bb721fde81a31d"))
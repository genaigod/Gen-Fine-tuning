import os
import shutil
import time
import traceback

# Kohya_ss_train_lora_dir = r"E:\devspace\kohya_ss_admin\train_res"
Kohya_ss_train_lora_dir = r"/root/kohya_ss_admin/train_res"
# Stable_Lora_dir = r"E:\devspace\kohya_ss_admin\aaaa"
Stable_Lora_dir = r"/usr/local/stable-diffusion-webui/models/Lora"
SCAN_INTERVAL = 30  # 扫描间隔时间，单位为秒

def get_max_suffix_file(files):
    """
    """
    max_file = None
    max_num = -1
    has_suffix_files = False

    for file in files:
        base_name, ext = os.path.splitext(file)
        if '-' in base_name:
            num_part = base_name.split('-')[-1]
            if num_part.isdigit():
                has_suffix_files = True
                num = int(num_part)
                if num > max_num:
                    max_num = num
                    max_file = file
        else:
            if not has_suffix_files:
                max_file = file

    return max_file

def scan_and_copy():
    if not os.path.exists(Stable_Lora_dir):
        os.makedirs(Stable_Lora_dir)
    target_files = set(os.listdir(Stable_Lora_dir))

    for root, dirs, files in os.walk(Kohya_ss_train_lora_dir):
        if "model" in dirs:
            model_dir = os.path.join(root, "model")
            print(model_dir)
            model_files = os.listdir(model_dir)

            model_files = [f for f in model_files if f.endswith('.safetensors') or f.endswith('.ckpt')]

            base_names = set()
            ori_names = set()
            model_files = [get_max_suffix_file(model_files)]
            print(model_dir, model_files)
            for file in model_files:
                print(file)
                ori_names.add(file)
                base_name, ext = os.path.splitext(file)
                if '-' in base_name:
                    base_name = base_name.split('-')[0] + ext
                else:
                    base_name = base_name + ext
                base_names.add(base_name)

            for index, base_name in enumerate(base_names):
                if base_name not in target_files:
                    max_file = base_name
                    if max_file:
                        src_file = os.path.join(model_dir, list(ori_names)[index])
                        dest_file = os.path.join(Stable_Lora_dir, base_name)
                        shutil.copy2(src_file, dest_file)
                        print(f"Copied {src_file} to {dest_file}")

def main():
    while True:
        try:
            scan_and_copy()
        except Exception as e:
            print(traceback.format_exc())
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()
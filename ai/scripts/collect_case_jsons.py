import os
import shutil

# 원본이 들어있는 루트 디렉토리들
source_roots = [
    'Training/01.원천데이터',
    'Validation/01.원천데이터'
]

# 모든 JSON을 모아둘 대상 디렉토리
dest_dir = 'all_json'
os.makedirs(dest_dir, exist_ok=True)

for root_dir in source_roots:
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower().endswith('.json'):
                src_path = os.path.join(dirpath, fname)
                dst_path = os.path.join(dest_dir, fname)

                # 중복 파일명 처리
                if os.path.exists(dst_path):
                    base, ext = os.path.splitext(fname)
                    i = 1
                    while True:
                        new_name = f"{base}_{i}{ext}"
                        new_dst = os.path.join(dest_dir, new_name)
                        if not os.path.exists(new_dst):
                            dst_path = new_dst
                            break
                        i += 1

                shutil.copy2(src_path, dst_path)

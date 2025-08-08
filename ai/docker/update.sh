#!/bin/bash
# 컨테이너 내에서 git pull 실행
docker exec dev-ai git pull origin master
docker exec dev-ai pip install -r requirements.txt
docker restart dev-ai
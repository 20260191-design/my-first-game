# Week 11 실습

## 오늘 한 것
- PyInstaller 설치 및 빌드
- resource_path() 함수 추가
- --add-data 옵션으로 에셋 포함
- .exe 실행 확인

## resource_path() 를 써야하는 이유
pyinstaller로 만든 exe에서 이미지,사운드 파일 경로가 바뀌기 때문이다

## 빌드 명령어
pyinstaller --oneflie space.surviver.py
pyinstaller --oneflie --windowed space.surviver.py
pyinstaller --oneflie --windowed --add-data "assets;assets" --name=space_surviver.py

## AI 활용 내역
pygame 빌드 과정중 오류 수정
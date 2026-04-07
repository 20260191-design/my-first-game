# 6주차 실습 기록

## 사용한 에셋
- 이미지: Tiny RPG Character Asset Pack -Demo Soldier&Orc (itch.io),
		 kenney_new-platformer-pack-1.1(kenney.nl)
- 사운드: Comedy Cartoon Funny Background Music (STARSTIN), 
		Cinematic Sound Effect (Diamond_Tunes)		// pixabay

## 사용한 AI 프롬프트 (요약)
1. convert_alpha() 없으면 어떻게 되는지
	Pygame에서 이미지 로드 시 convert_alpha()를 안 쓰면 투명 픽셀이 깨지거나 성능이 떨어질 수 있	다는 질문.
2. 이미지가 화면 밖으로 나가면 반대편에서 다시 나오게 코드 수정
	이동하는 이미지가 화면 끝을 넘어가면 반대편에서 다시 나타나도록 처리하는 방법 문의.
3. 사운드 관련 질문
	Pygame에서 사운드를 재생하거나 제어하는 방법 관련 질문.
4. 애니메이션 코드 관련 질문
	Sprite를 이용해 간단한 애니메이션 구현 설명

## AI 답변에서 도움이 된 것
covert_alpha에 대해서 자세히 알게되었다
sprite 애니메이션 관련 코드가 어떤식으로 작동하는지 알게되었다

## AI 답변을 수정하거나 버린 것
마우스를 클릭하였을때 소리나는 부분에 소리에 딜레이가 심하게 들어가 버리고 다시 짯다

## 적용 결과
- 잘 된 것: 배경음과 클릭했을때 사운드가 잘 나온다
- 어려웠던 것: 사운드에 딜레이가 좀 걸려 어려웠다
- 다음에 시도할 것 애니메이션을 더 다양하게 시도해보고 싶다

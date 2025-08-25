<template>
  <section class="ruling-hero">
    <div class="ruling-container">
      <p class="eyebrow"><strong>두번째</strong>, 판례 찾아보기</p>

      <h2 class="title">
        <span><strong>원하는</strong> 판례를 찾아내는</span><br />
        <span><strong>정확한</strong> 검색 기능!</span>
      </h2>

      <p class="desc">
        복잡하고 어려운 판례 검색, 몇 번의 클릭만으로<br/>원하는 결과를 가장 쉽고 빠르게 찾아드립니다.
      </p>

      <RouterLink to="/cases/search" class="cta cta--light">
        바로가기
      </RouterLink>
    </div>
  </section>
</template>


<style scoped>
:root {
  --navy: #1d2b50;
}

/* 섹션 래퍼: 배경 이미지를 섹션 전체로 */
.ruling-hero {
  position: relative;
  width: 100%;
  min-height: 520px;
  background: url('@/assets/section3Bg.png') center / cover no-repeat; /* 정적 배경 */
  display: flex;
  align-items: center;
}

/* 좌측 텍스트 컨테이너 */
.ruling-container {
  width: 100%;
  max-width: 1120px;
  margin: 0 auto;
  color: #eaf2ff; /* 다크 배경 위 가독 색 */
}

.eyebrow {
  font-size: 20px;
  letter-spacing: -0.2px;
  margin-bottom: 15px;
}

.title {
  margin: 0 0 30px;
  font-weight: 400;
  line-height: 1.25;
  letter-spacing: -0.3px;
  color: #ffffff;
  font-size: clamp(28px, 4.3vw, 44px);
}

.desc {
  max-width: 520px;
  margin: 0 0 22px;
  font-size: 15px;
  line-height: 1.65;
  color: #cfcfcf ;
}

/* CTA 버튼 */
.cta {
  display: inline-block;
  margin: 16px auto 0;
  padding: 12px 22px;
  min-width: 200px;
  text-decoration: none;
  border-radius: 999px;
  background: #fff;
  color: #1d2b50;
  font-weight: 600;
  box-shadow: none;
  text-align: center;
}

/* 반응형 여백 조정 */
@media (min-width: 1200px) {
  .ruling-container { padding-left: 32px; }
}
</style>

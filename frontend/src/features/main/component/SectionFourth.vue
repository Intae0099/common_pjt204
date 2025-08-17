<template>
  <section class="lawyer-hero">
    <div class="wrap">
      <div class="copy">
        <p class="eyebrow"><strong>세번째,</strong> 추천받은 변호사 조회하기</p>
        <h2 class="title">
          <span class="em">나에게 가장 적합한 변호사</span><br />
          AI가 찾아드립니다
        </h2>
        <p class="desc">
          AI가 가장 관련성 높은 법률 전문가를 추천해 드립니다.<br />
          또는 분야별로 원하는 변호사를 직접 검색해보세요
        </p>
      </div>

      <div class="visual" aria-hidden="true">
        <img class="laptop" src="@/assets/section4-laptop.png" alt="" />
      </div>

      <div class="tag-marquees">
        <div class="marquee to-right" aria-hidden="true">
          <div class="track">
            <div class="content">
              <span class="tag"># 교통·사고·보험</span>
              <span class="tag"># 가사·가족</span>
              <span class="tag"># 민사·계약·채권</span>
              <span class="tag"># 파산·회생·채무조정</span>
              <span class="tag"># 상송·증여</span>
            </div>
            <div class="content" aria-hidden="true">
              <span class="tag"># 교통·사고·보험</span>
              <span class="tag"># 가사·가족</span>
              <span class="tag"># 민사·계약·채권</span>
              <span class="tag"># 파산·회생·채무조정</span>
              <span class="tag"># 상송·증여</span>
            </div>
          </div>
        </div>

        <div class="marquee to-left" aria-hidden="true">
          <div class="track">
            <div class="content">
              <span class="tag"># 지식재산권</span>
              <span class="tag"># 노동·고용</span>
              <span class="tag"># 행정·조세</span>
              <span class="tag"># 의료·생명·개인정보</span>
              <span class="tag"># 환경·공공</span>
              <span class="tag"># 금융·증권·기업</span>
            </div>
            <div class="content" aria-hidden="true">
              <span class="tag"># 지식재산권</span>
              <span class="tag"># 노동·고용</span>
              <span class="tag"># 행정·조세</span>
              <span class="tag"># 의료·생명·개인정보</span>
              <span class="tag"># 환경·공공</span>
              <span class="tag"># 금융·증권·기업</span>
            </div>
          </div>
        </div>
      </div>

      <RouterLink to="/lawyers" class="cta">바로가기</RouterLink>
    </div>
  </section>
</template>

<style scoped>
.lawyer-hero{
  position: relative;
  width: 100%;
  background: #fff;
  /* 노트북이 아래로 살짝 튀어나오니 바닥 여백 조금 추가 */
  padding: clamp(48px, 6vw, 96px) 0 120px;
}
.wrap{
  position: relative; /* 절대배치 기준점 */
  margin: 0 auto;
  max-width: 1120px;
  padding: 0 20px;
  /* 그리드/좌우배치 제거: 요청대로 상단 카피 -> 태그 순서 유지 */
  display: block;
}

.copy{ position: relative; z-index: 3; } /* 텍스트가 가장 위 */
.copy .eyebrow{ font-size:20px; letter-spacing:-.2px; color:#1d2b50; margin-bottom:15px; }
.title{ margin:0 0 30px; font-size:clamp(28px,4.2vw,44px); font-weight:400; letter-spacing:-.3px; color:#1d2b50; line-height:1.25; }
.title .em{ font-weight:800; }
.desc{ margin:0 0 22px; color:#5a6b84; line-height:1.65; max-width:520px; }

.cta{
  display:inline-block; margin:30px auto 0; border-radius:100px; padding:12px 22px;
  min-width:200px; text-align:center; text-decoration:none; background:#1d2b50; color:#fff; font-weight:700;
  position: relative; z-index: 4; /* 버튼이 노트북/태그 위 */
}

/* 노트북 비주얼: 태그 위로 겹치기 */
.visual{
  position: absolute;
  right: -90px;        /* 살짝 화면 밖으로 빼서 크게 보이게 */
  top: 45px;       /* 태그 라인 위로 살짝 겹침 */
  z-index: 2;          /* 태그(1)보다 위, 카피(3)보다 아래 */
  pointer-events: none;/* 클릭 가로막지 않게 */
}
.laptop{
  width: clamp(540px, 70vw, 1000px);
  height: auto;
  display: block;
  filter: drop-shadow(0 40px 60px rgba(23,36,64,.18));
}

/* 태그 스크롤 (그대로) */
.tag-marquees{
  position: relative;
  z-index: 1; /* 노트북 아래로 */
  display: grid; gap:14px; margin-top: 28px;
}
.marquee{
  --gap:14px; --speed:26s;
  position: relative; overflow:hidden; width:100%;
  -webkit-mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
  mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
}
.track{ display:flex; width:max-content; animation:scroll var(--speed) linear infinite; }
.to-right .track{ animation-direction: reverse; }
.to-left .track{  animation-direction: normal; }
.content{ display:flex; gap:var(--gap); padding-right:var(--gap); }
.tag{
  display:inline-block; white-space:nowrap; padding:10px 16px; border-radius:999px;
  border:1px solid #6c9acf3d; background:#fff; color:#6c9acf3d; font-weight:400; font-size:20px; letter-spacing:-.2px;
}
@keyframes scroll{ from{transform:translateX(0)} to{transform:translateX(-50%)} }
@media (prefers-reduced-motion: reduce){ .track{animation:none !important} }

/* 모바일: 겹침 대신 자연 배치 */
@media (max-width: 1024px){
  .visual{ position: static; margin: 16px auto 0; z-index: 0; }
  .laptop{ width:min(92vw, 720px); }
}
</style>

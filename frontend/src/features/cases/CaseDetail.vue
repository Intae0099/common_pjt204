<!-- src/pages/case/CaseDetail.vue -->
<template>
  <CaseLayout>
    <div class="text-wrapper-9 back-button" @click="goBack">이전</div>
    <div v-if="isLoading" class="status-message">
      <p>판례 정보를 불러오는 중입니다...</p>
    </div>
    <div v-else-if="error" class="status-message error">
      <p>{{ error }}</p>
    </div>
  <!-- 데이터가 로드된 후에만 전체 내용을 보여줍니다. -->
     <div v-else-if="caseData" class="case-detail-container">

      <!-- '이전' 버튼: 클릭 시 뒤로 갑니다. -->


      <div class="rectangle-3"></div>

      <!-- 제목 -->
      <p class="text-wrapper-10">{{ caseData.title }}</p>

      <div class="text-wrapper-12">사건번호</div>
      <div class="text-wrapper-19">{{ caseData.caseNumber }}</div>

      <div class="text-wrapper-17">사건종류</div>
      <div class="text-wrapper-23">{{ caseData.category }}</div>

      <div class="text-wrapper-18">선고일자</div>
      <div class="text-wrapper-24">{{ caseData.decisionDate }}</div>

      <!-- 참조 법령 -->
      <div class="overlap">
        <div class="text-wrapper-13">
          참조 법령
          <br />
          조문 목록
        </div>
        <!-- v-html을 사용하여 <br> 태그가 렌더링되도록 합니다. -->
        <p class="text-wrapper-14" v-html="caseData.statutes"></p>
      </div>

      <!-- 판시사항 -->
      <div class="text-wrapper-15">판시사항</div>
      <p class="text-wrapper-20" v-html="caseData.issue"></p>

      <!-- 판결요지 -->
      <div class="text-wrapper-16">판결요지</div>
      <p class="text-wrapper-21" v-html="caseData.summary"></p>

      <!-- 판례전문 -->
      <div class="text-wrapper-11">판례전문</div>
      <p class="text-wrapper-22" v-html="caseData.fullText"></p>

    </div>
    <!-- 데이터가 로드되기 전이나 없을 때 보여줄 메시지 -->
    <div v-else>
      <p>판례 정보를 불러오는 중입니다...</p>
    </div>
  </CaseLayout>
</template>

<script setup>
import CaseLayout from '@/components/layout/CaseLayout.vue';
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fastapiApiClient } from '@/lib/axios';

// 라우트 정보와 라우터 인스턴스를 가져옵니다.
const route = useRoute();
const router = useRouter();
// 판례 상세 데이터를 담을 ref
const caseData = ref(null);
const isLoading = ref(true);
const error = ref(null);


// 뒤로 가기 함수
const goBack = () => {
  router.go(-1);
};

// API 응답에 <br> 태그 등이 이미 포함되어 있을 수 있으므로,
// 추가 변환 없이 그대로 사용하거나, 필요 시 줄바꿈 문자를 <br>로 변환
const formatHtml = (text) => {
  if (!text) return '';
  // 예시: API 응답이 순수 텍스트이고 줄바꿈(\n)이 있다면 <br>로 변환
  // return text.replace(/\n/g, '<br />');
  return text; // API 응답을 믿고 그대로 반환
};

onMounted(async () => {
  const precId = route.params.id;
  if (!precId) {
    error.value = '잘못된 접근입니다. 판례 ID가 없습니다.';
    isLoading.value = false;
    return;
  }

  try {
    isLoading.value = true;
    error.value = null;

    // ✨ fastapiApiClient를 사용하여 호출합니다.
    const response = await fastapiApiClient.get(`/cases/${precId}`);

    if (response.data.success) {
      caseData.value = response.data.data;
    } else {
      throw new Error(response.data.error.message);
    }
  } catch (err) {
    console.error('판례 상세 조회 실패:', err);
    if (err.response?.status === 404) {
      error.value = '해당 판례를 찾을 수 없습니다.';
    } else {
      error.value = err.response?.data?.error?.message || '정보를 불러오는 데 실패했습니다.';
    }
  } finally {
    isLoading.value = false;
  }
});

/*
// 백엔드 API를 대체할 더미 데이터베이스
const dummyDB = [
  {
    id: '1', // URL 파라미터는 문자열이므로 id도 문자열로 맞추는 것이 안전합니다.
    title: '유언효력확인의소[녹음에 의한 유언의 효력 확인을 구한 사건]',
    caseNumber: '대법원 2023. 6. 1. 선고 2023다215537 판결', // 사건번호를 더 명확하게 수정
    category: '민사',
    decisionDate: '2023-06-01',
    statutes: `[1]민법 제1067조, 제1073조, 민사소송법 제288조, 제355조 <br />[2]민사소송법 제202조`,
    issue: `[1] 유언증서가 성립한 후에 멸실되거나 분실된 경우, 이해관계인이 유언증서의 내용을 증명하여 유언의 유효를 주장할 수 있는지 여부(적극) 및 이는 녹음에 의한 유언이 성립한 후에 녹음테이프나 녹음파일 등이 멸실 또는 분실된 경우에도 마찬가지인지 여부(적극) / 원본의 존재 및 원본 성립의 진정에 관하여 다툼이 있고 사본을 원본의 대용으로 하는 것에 대하여 상대방으로부터 이의가 있는 경우, 사본으로써 원본을 대신할 수 있는지 여부(소극) 및 서증으로서 사본 제출의 효과 / 서증 제출에 있어 원본을 제출할 필요가 없는 경우 및 그 주장·증명책임의 소재(=해당 서증의 신청당사자)
      <br /><br />
      [2] 감정인의 감정 결과의 증명력`,
    summary: `[1] 유언증서가 성립한 후에 멸실되거나 분실되었다는 사유만으로 유언이 실효되는 것은 아니고 이해관계인은 유언증서의 내용을 증명하여 유언의 유효를 주장할 수 있다. 이는 녹음에 의한 유언이 성립한 후에 녹음테이프나 녹음파일 등이 멸실 또는 분실된 경우에도 마찬가지이다. ... (이하 생략)`,
    fullText: `【원고, 피상고인】 원고 1 외 2인 (소송대리인 법무법인 서휘 담당변호사 김익현 외 5인) <br />【피고, 상고인】 피고 (소송대리인 법무법인 가람 외 1인) <br />【원심판결】 서울고법 2023. 2. 1. 선고 2021나2035828 판결 ... (이하 생략)`
  },
  {
    id: '2',
    title: '손해배상 청구 사건 (예시)',
    caseNumber: '대법원 2022. 5. 1. 선고 2022다12345 판결',
    category: '민사',
    decisionDate: '2022-05-01',
    statutes: `민법 제750조`,
    issue: `불법행위로 인한 손해배상 책임의 성립 요건에 관한 판시사항입니다.`,
    summary: `고의 또는 과실로 인한 위법행위로 타인에게 손해를 가한 자는 그 손해를 배상할 책임이 있다.`,
    fullText: `손해배상 청구 사건의 상세 전문 내용입니다.`
  },
  // 다른 판례 데이터 추가 가능
];

onMounted(() => {
  // 현재 URL에서 'id' 파라미터를 가져옵니다.
  const currentCaseId = route.params.id;

  // 더미 데이터베이스에서 해당 id를 가진 판례를 찾습니다.
  // 실제 애플리케이션에서는 이 부분에서 API를 호출합니다.
  // 예: const response = await fetch('/api/cases/' + currentCaseId);
  //     caseData.value = await response.json();
  caseData.value = dummyDB.find(item => item.id === currentCaseId);
});
*/
</script>

<template>
  <!-- v-if="userInfo"를 추가하여 데이터가 로드된 후에만 화면이 보이도록 처리 -->
  <div v-if="userInfo" class="mypage-container">
    <div class="text-wrapper-4">마이페이지</div>
    <div class="element">
      <div class="div">
        <!-- 사용자 정보 섹션 -->
        <div class="overlap">
          <img class="img" alt="Profile" />
          <div class="text-wrapper">{{ userInfo.name }}</div>
          <div class="ellipse"></div>
          <div class="text-wrapper-2">{{ userInfo.birthdate }}</div>
          <div class="text-wrapper-3">계정설정</div>
        </div>
        <hr>

        <!-- 예약일정 섹션 (v-for 활용) -->
        <div class="text-wrapper-5">예약일정</div>
        <!-- 예약이 없을 경우 메시지를 보여줄 수 있습니다. -->
        <div v-if="reservationList.length === 0" class="no-reservations">
          예약된 일정이 없습니다.
        </div>
        <!-- v-for를 사용해 예약 목록을 반복 렌더링 -->
        <div v-for="item in reservationList" :key="item.id">
          <div class="overlap-group">
            <div class="text-wrapper-6">{{ item.title }}</div>
            <div class="text-wrapper-7">{{ item.date }}</div>
            <div class="east">
              <img class="vector" alt="Vector" :src="vector5" />
            </div>
          </div>
          <hr>
        </div>

        <!-- 고정 메뉴들 -->
        <div class="text-wrapper-8">상담신청서 보관함</div>
        <hr>
        <div class="text-wrapper-9">상담내역</div>
        <hr>

        <!-- 결제내역 섹션 (기존 코드 유지) -->
        <div class="text-wrapper-10">결제내역</div>
        <hr>
        <div class="text-wrapper-10">회원탈퇴</div>
        </div>
    </div>
  </div>
  <!-- 데이터 로딩 중 표시될 화면 -->
  <div v-else>
    마이페이지 정보를 불러오는 중입니다...
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

// --- 이미지 import ---
// 실제 프로젝트의 이미지 경로에 맞게 수정해주세요.
// import x03 from '@/assets/images/profile_icon.png';
// import vector from '@/assets/images/vector.svg';
// import vector5 from '@/assets/images/vector5.svg';

// --- 데이터 상태 정의 ---
// 1. 사용자 정보를 담을 객체 (처음에는 null로 초기화)
const userInfo = ref(null);

// 2. 예약 일정 목록을 담을 배열
const reservationList = ref([]);

// 3. 변호사 상담 내역 목록을 담을 배열 (기존 lawyers 데이터)
// const lawyers = ref([]);


// --- 데이터 로딩 (onMounted 훅 사용) ---
// 컴포넌트가 화면에 마운트된 후 실행됩니다.
onMounted(() => {
  // 실제로는 이 곳에서 백엔드 API를 호출합니다.
  // 예: const data = await fetch('/api/mypage').then(res => res.json());

  // 지금은 더미 데이터로 시뮬레이션합니다.
  // 1. 사용자 정보 데이터 주입
  userInfo.value = {
    name: '홍길동',
    birthdate: '2001.06.23',
    // profileImage: x03, // import한 이미지 변수 사용
  };

  // 2. 예약 일정 데이터 주입 (여러 개)
  reservationList.value = [
    { id: 1, title: '사건1 상담신청서 예시제목', date: '2025-04-16' },
    { id: 2, title: '부동산 계약 관련 긴급 상담', date: '2025-04-20' },
    { id: 3, title: '손해배상 청구 자문', date: '2025-05-01' },
  ];

  // 3. 변호사 상담 내역 데이터 주입
  // lawyers.value = [
  //   { id: 1, name: '김변호', date: '2024-03-15', status: '상담완료' },
  //   { id: 2, name: '이변호', date: '2024-03-20', status: '상담완료' },
  //   { id: 3, name: '박변호', date: '2024-04-01', status: '결제완료' },
  // ];
});
</script>

<style scoped>
/* 여기에 기존 CSS를 그대로 두시면 됩니다. */
.no-reservations {
  padding: 20px;
  text-align: center;
  color: #888;
}
</style>

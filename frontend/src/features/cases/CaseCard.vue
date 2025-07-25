<template>
  <!-- 각 카드 아이템을 감싸는 루트 div -->
   <router-link
    :to="{ name: 'CaseDetail', params: { id: data.id } }"
    class="card-link"
  >
  <div class="case-card-container">
    <!-- CaseCard의 원래 내용이 여기에 올 수 있습니다. -->
    <!-- 예를 들어, 부모로부터 받은 데이터를 표시하는 부분 -->

    <!-- 이 부분이 각 카드마다 반복되기를 원하셨던 UI 입니다. -->
    <div class="overlap">
      <div class="keyboard-arrow-down">
        <!-- vector 이미지는 props로 받거나 직접 경로를 지정할 수 있습니다. -->
        <!-- <img class="vector-2" alt="Vector" src="@/assets/vector.svg" /> -->
      </div>
    </div>
    <div class="overlap-2">
      <div class="group-3">
        <div class="group-4">
          <!-- props로 받은 데이터를 여기에 바인딩합니다. -->
          <div class="text-wrapper-11">{{ data.title }}</div>
          <p class="text-wrapper-12">
            {{ data.summary }}
          </p>
        </div>
      </div>
      <hr/>
    </div>
  </div>
  </router-link>
</template>

<script setup>
// 부모 컴포넌트(CaseSearchPage)로부터 'data'라는 이름의 prop을 받습니다.
// 이 data는 { id: 1, title: '...', summary: '...' } 형태의 객체입니다.
defineProps({
  data: {
    type: Object,
    required: true
  }
})

// 이미지 경로를 props로 받지 않을 경우, 여기서 직접 import 할 수도 있습니다.
// import vector from '@/assets/images/vector.svg' // 실제 이미지 경로로 수정하세요
</script>

<style scoped>
a {
  text-decoration: none;
  color: inherit;
}
.group-4{
  text-decoration: none;
}
.text-wrapper-11{
  font-size: 1.4rem;
  font-weight: bold;
  margin-bottom: 10px;
}
.text-wrapper-12{
  font-size: 1rem;
}
</style>

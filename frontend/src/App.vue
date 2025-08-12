<template>
  <component :is="layoutComponent" :key="$route.name">
    <RouterView :key="$route.fullPath" />
  </component>
</template>


<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import LayoutDefault from '@/components/layout/LayoutDefault.vue'
const route = useRoute()

// 배너가 있는 페이지 경로
const noLayoutNames = ['Main','CasesSearch', 'CaseDetail','ConsultForm','MeetingRoom']
const layoutComponent = computed(() => {
  return noLayoutNames.includes(route.name) ? 'div' : LayoutDefault
})
</script>

<style scoped>

</style>


<template>
  <component :is="layoutComponent">
    <RouterView />
  </component>
</template>


<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import LayoutDefault from '@/components/layout/LayoutDefault.vue'
const route = useRoute()

// 배너가 있는 페이지 경로
const noLayoutNames = ['CasesSearch', 'CaseDetail','ConsultForm']
const layoutComponent = computed(() => {
  return noLayoutNames.includes(route.name) ? 'div' : LayoutDefault
})
</script>

<style scoped>

</style>


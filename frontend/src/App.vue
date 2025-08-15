<template>
  <component :is="layoutComponent" :key="$route.name">
    <RouterView :key="$route.fullPath" />
  </component>
  <BaseFooter v-if="!hideFooter"/>
</template>


<script setup>
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import LayoutDefault from '@/components/layout/LayoutDefault.vue'
import BaseFooter from './components/BaseFooter.vue'
const route = useRoute()

// 배너가 있는 페이지 경로
const noLayoutNames = ['Main','CasesSearch', 'CaseDetail','ConsultForm','MeetingRoom']

const isAdminRoute = computed(() => route.path.startsWith('/admin'))

const layoutComponent = computed(() => {
  return (noLayoutNames.includes(route.name) || isAdminRoute.value) ? 'div' : LayoutDefault
})

// 푸터 숨김 여부
const hideFooter = computed(() => route.matched.some(r => r.meta?.hideFooter))
</script>

<style scoped>

</style>


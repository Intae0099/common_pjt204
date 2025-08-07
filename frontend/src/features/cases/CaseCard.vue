<template>
   <router-link
    :to="{ name: 'CaseDetail', params: { id: data.caseId } }"
    class="card-link"
  >
  <div class="case-card-container">
    <div class="overlap">
      <div class="keyboard-arrow-down">
      </div>
    </div>
    <div class="overlap-2">
      <div class="group-3">
        <div class="group-4">
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
defineProps({
  data: {
    type: Object,
    required: true
  }
})

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

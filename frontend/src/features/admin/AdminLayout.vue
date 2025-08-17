<template>
  <div class="admin-container">
    <aside class="admin-sidebar">
      <img class="logo-image" src="@/assets/logo-white.png" alt="에이로로고">
      <h2>관리자 메뉴</h2>
      <nav>
        <ul>
          <li>
            <router-link :to="{ name: 'admin-lawyer-management' }">변호사 인증 관리</router-link>
          </li>
          <li>
            <router-link :to="{ name: 'admin-clients' }">전체 회원 목록</router-link>
          </li>
          <li>
            <router-link :to="{ name: 'admin-lawyer-certificate' }">전체 변호사 목록</router-link>
          </li>
          <li>
            <router-link :to="{ name: 'admin-room-management' }">상담방 관리</router-link>
          </li>
        </ul>
      </nav>
    </aside>
    <main class="admin-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.admin-container {
  display: flex;
  min-height: 100vh;
  font-family: 'Noto Sans KR', sans-serif;
}
.logo-image {
  width: 150px;
  margin-left: 7px;
}
.admin-sidebar {
  flex: 0 0 220px;
  width: 220px;
  background-color: #1d2b50;
  color: white;
  padding: 60px 20px 20px 20px;
}
.admin-sidebar h2 {
  margin-top: 10px;
  margin-left: 10px;
  /* text-align: center; */
}
.admin-sidebar nav ul {
  list-style: none;
  padding: 0;
}
.admin-sidebar nav li a {
  display: block;
  padding: 10px 15px;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  margin-bottom: 5px;
}
.admin-sidebar nav li a:hover,
.router-link-exact-active { /* 현재 활성화된 링크 스타일 */
  color: #6c9bcf;
}

.admin-content {
  flex-grow: 1;
  padding: 40px;
  background-color: #f1f1f1;
  font-family: 'Noto Sans KR', sans-serif;
  color: #333
}
</style>

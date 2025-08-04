<template>
  <div class="admin-container">
    <aside class="admin-sidebar">
      <h2>관리자 메뉴</h2>
      <nav>
        <ul>
          <li>
            <!-- name을 사용한 라우터 링크 -->
            <router-link :to="{ name: 'admin-lawyer-management' }">변호사 인증 관리</router-link>
          </li>
          <li>
            <router-link :to="{ name: 'admin-clients' }">전체 회원 목록</router-link>
          </li>
          <li>
            <router-link :to="{ name: 'admin-room-management' }">상담방 관리</router-link>
          </li>
        </ul>
      </nav>
    </aside>
    <main class="admin-content">
      <!-- 자식 라우트의 컴포넌트가 이 자리에 렌더링됩니다. -->
      <router-view />
    </main>
  </div>
</template>

<script setup>
// 이 컴포넌트는 레이아웃 역할만 하므로 스크립트는 비워둬도 됩니다.
</script>

<style scoped>
.admin-container {
  display: flex;
  min-height: 100vh;
}
.admin-sidebar {
  width: 240px;
  background-color: #2c3e50;
  color: white;
  padding: 20px;
}
.admin-sidebar h2 {
  margin-top: 0;
  text-align: center;
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
  background-color: #34495e;
}
.admin-content {
  flex-grow: 1;
  padding: 20px;
  background-color: #f4f6f9;
}
</style>
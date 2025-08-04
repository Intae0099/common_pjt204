<template>
  <div class="login-wrapper">
    <h1 class="login-title">로그인</h1>
    <div class="login-box">
      <button class="kakao-login" @click="login">
        <img src="@/assets/kakao-icon.png" alt="카카오 아이콘" class="kakao-icon" />
        카카오 로그인
      </button>
      <div class="divider">변호사이신가요?</div>
      <router-link to="/login/lawyer">
        <button class="lawyer-login">변호사로 로그인</button>
      </router-link>
    </div>

    <div class="footer-links">
      <router-link :to="{ name: 'SignUpFirst' }">변호사 회원가입하기</router-link>
    </div>
  </div>
</template>

<script setup>

const login = async () => {

  window.location.href = 'https://i13b204.p.ssafy.io/oauth2/authorization/kakao'
}
</script>


<style scoped>
*{
  font-family: 'Noto Sans KR', sans-serif;
}
.login-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 200px;
  font-family: 'Pretendard', sans-serif;
}

.login-title {
  font-size: 24px;
  margin-bottom: 40px;
  font-weight: bold;
}

.login-box {
  width: 400px;
  background-color: white;
  border: 1px solid #E4EEF5;
  border-radius: 10px;
  padding: 40px 30px;
  box-shadow: 0 1px 5px #E4EEF5;
  text-align: center;
}
.kakao-login {
  background-color: #FBE300;
  border: none;
  color: #381e1f;
  font-weight: bold;
  padding: 12px;
  width: 100%;
  border-radius: 6px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 30px;
  cursor: pointer;
}

.kakao-icon {
  width: 24px;
  height: 24px;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  font-size: 13px;
  color: #aaa;
  margin-bottom: 16px;
}
.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e0e0e0;
  margin: 0 12px;
}
.lawyer-login {
  background-color: #0c2c46;
  color: white;
  border: none;
  padding: 12px;
  width: 100%;
  border-radius: 6px;
  font-weight: bold;
  font-size: 15px;
  cursor: pointer;
}
.footer-links {
  margin-top: 12px;
  font-size: 13px;
  color: #777;
  display: flex;
}
</style>

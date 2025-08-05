package com.B204.lawvatar_backend.common.config;

import com.B204.lawvatar_backend.user.admin.service.AdminService;
import java.util.List;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.ProviderManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

@Configuration
public class AdminAuthConfig {

  @Bean(name = "adminAuthenticationManager")
  public AuthenticationManager adminAuthenticationManager(
      AdminService adminService
  ) {
    // 오직 AdminService 만 등록된 ProviderManager 생성
    return new ProviderManager(List.of(adminAuthProvider(adminService)));
  }

  @Bean
  public DaoAuthenticationProvider adminAuthProvider(AdminService adminService) {
    DaoAuthenticationProvider p = new DaoAuthenticationProvider();
    p.setUserDetailsService(adminService);
    p.setPasswordEncoder(new BCryptPasswordEncoder());
    return p;
  }
}

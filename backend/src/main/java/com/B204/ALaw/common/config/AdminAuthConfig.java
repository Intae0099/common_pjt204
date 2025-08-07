package com.B204.ALaw.common.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.ProviderManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.crypto.password.PasswordEncoder;

import com.B204.ALaw.user.admin.service.AdminService;

@Configuration
public class AdminAuthConfig {

  /**
   * Admin 전용 DaoAuthenticationProvider
   */
  @Bean
  public DaoAuthenticationProvider adminAuthProvider(
      AdminService adminService,
      PasswordEncoder passwordEncoder) {
    DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
    provider.setUserDetailsService(adminService);
    provider.setPasswordEncoder(passwordEncoder);
    return provider;
  }

  /**
   * Admin용 AuthenticationManager (ProviderManager)
   */
  @Bean(name = "adminAuthenticationManager")
  public AuthenticationManager adminAuthenticationManager(
      DaoAuthenticationProvider adminAuthProvider) {
    return new ProviderManager(adminAuthProvider);
  }
}

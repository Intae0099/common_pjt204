package com.B204.ALaw.user.admin.service;

import com.B204.ALaw.user.admin.entity.Admin;
import com.B204.ALaw.user.admin.repository.AdminRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AdminService implements UserDetailsService {

  private final AdminRepository adminRepo;

  @Override
  public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
    Admin admin = adminRepo.findByLoginEmail(email)
        .orElseThrow(() -> new UsernameNotFoundException("관리자 계정을 찾을 수 없습니다."));

    return new org.springframework.security.core.userdetails.User(
        admin.getLoginEmail(),
        admin.getPasswordHash(),
        AuthorityUtils.createAuthorityList("ROLE_ADMIN")
    );
  }

  public Admin findByLoginEmail(String email) {
    return adminRepo.findByLoginEmail(email)
        .orElseThrow(() -> new UsernameNotFoundException("관리자 계정을 찾을 수 없습니다."));
  }

}
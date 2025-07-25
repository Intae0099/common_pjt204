package com.B204.lawvatar_backend.user.lawyer.service;

import com.B204.lawvatar_backend.user.lawyer.entity.CertificationStatus;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import com.B204.lawvatar_backend.user.lawyer.repository.LawyerRepository;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
public class LawyerService implements UserDetailsService {

  private final LawyerRepository repo;
  public LawyerService(LawyerRepository repo) {
    this.repo = repo;
  }

  @Override
  public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
    Lawyer lawyer = repo.findByLoginEmail(username)
        .orElseThrow(() -> new UsernameNotFoundException("변호사 계정이 없습니다이"));

    if(lawyer.getCertificationStatus() != CertificationStatus.APPROVED) {
      throw new BadCredentialsException("인증되지 않은 계정입니다. 관리자에게 문의하세요.");
    }

    return new org.springframework.security.core.userdetails.User(
        lawyer.getLoginEmail(),
        lawyer.getPasswordHash(),
        AuthorityUtils.createAuthorityList("ROLE_LAYWER")
    );
  }

  public Lawyer findByLoginEmail(String loginEmail) {
    return repo.findByLoginEmail(loginEmail)
        .orElseThrow(() -> new UsernameNotFoundException("Lawyer not found: " + loginEmail));
  }

}


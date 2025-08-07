package com.B204.ALaw.common.principal;

import com.B204.ALaw.user.lawyer.entity.Lawyer;
import com.B204.ALaw.user.lawyer.entity.LawyerTag;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

public class LawyerPrincipal implements UserDetails {

  private final Lawyer lawyer;

  // 생성자: Lawyer 엔티티만 받습니다.
  public LawyerPrincipal(Lawyer lawyer) {
    this.lawyer = lawyer;
  }

  @Override
  public Collection<? extends GrantedAuthority> getAuthorities() {
    return Collections.emptyList();
  }

  @Override
  public String getPassword() {
    return null;
  }

  @Override
  public String getUsername() {
    return lawyer.getLoginEmail().toString();
  }
  
  public Long getId(){
    return lawyer.getId();
  }

  public String getIntroduction(){
    return lawyer.getIntroduction();
  }

  public String getExam() {
    return lawyer.getExam();
  }

  public String getRegistrationNumber(){
    return lawyer.getRegistrationNumber();
  }

  public int getConsultationCount(){
    return lawyer.getConsultationCount();
  }

  public List<LawyerTag> getTags(){
    return lawyer.getTags();
  }

  @Override
  public boolean isAccountNonExpired() {
    return true;
  }

  @Override
  public boolean isAccountNonLocked() {
    return true;
  }

  @Override
  public boolean isCredentialsNonExpired() {
    return true;
  }

  @Override
  public boolean isEnabled() {
    return true;
  }

  // 편의 메서드
  public String getName() {
    return lawyer.getName();
  }
}
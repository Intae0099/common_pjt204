package com.B204.ALaw.common.principal;

import com.B204.ALaw.user.client.entity.Client;
import java.util.Collection;
import java.util.Collections;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

public class ClientPrincipal implements UserDetails {

  private final Client client;

  // 생성자: User 엔티티만 받습니다.
  public ClientPrincipal(Client client) {
    this.client = client;
  }

  // == UserDetails 메서드 최소 구현 ==
  @Override
  public Collection<? extends GrantedAuthority> getAuthorities() {
    // roles 사용 안 하므로 빈 리스트
    return Collections.emptyList();
  }

  @Override
  public String getPassword() {
    // JWT 인증만 쓰므로 비어 있어도 됩니다.
    return null;
  }

  @Override
  public String getUsername() {
    // subject 로 설정한 ID
    return client.getId().toString();
  }

  public Long getId(){
    return client.getId();
  }

  public String getOauthtName() {
    return client.getOauthName();
  }

  public String getOauthProvider(){
    return client.getOauthProvider();
  }

  public String getOauthIndentifier(){
    return client.getOauthIdentifier();
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
  public String getEmail() {
    return client.getEmail();
  }
}

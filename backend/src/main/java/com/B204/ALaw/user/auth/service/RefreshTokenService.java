package com.B204.ALaw.user.auth.service;

import com.B204.ALaw.user.admin.entity.Admin;
import com.B204.ALaw.user.auth.entity.RefreshToken;
import com.B204.ALaw.user.auth.repository.RefreshTokenRepository;
import com.B204.ALaw.user.client.entity.Client;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import jakarta.transaction.Transactional;
import java.time.LocalDateTime;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class RefreshTokenService {

  private final RefreshTokenRepository repo;
  private final long refreshExpirationMs;

  public RefreshTokenService(
      RefreshTokenRepository repo,
      @Value("${jwt.refresh-expiration}") long refreshExpirationMs
  ) {
    this.repo = repo;
    this.refreshExpirationMs = refreshExpirationMs;
  }

  @Transactional
  public RefreshToken createForClient(Client client, String rawToken) {
    // 기존 토큰 전부 삭제
    repo.deleteByClient(client);
    // 새 토큰 저장
    RefreshToken rt = RefreshToken.ofForClient(client, rawToken, LocalDateTime.now(), refreshExpirationMs);
    return repo.save(rt);
  }

  @Transactional
  public RefreshToken createForLawyer(Lawyer lawyer, String rawToken) {
    // 기존 토큰 전부 삭제
    repo.deleteByLawyer(lawyer);
    // 새 토큰 저장
    RefreshToken rt = RefreshToken.ofForLawyer(lawyer, rawToken, LocalDateTime.now(), refreshExpirationMs);
    return repo.save(rt);
  }

  @Transactional
  public RefreshToken createForAdmin(Admin admin, String rawToken) {
    // 기존 토큰 전부 삭제
    repo.deleteByAdmin(admin);
    // 새 토큰 저장
    RefreshToken rt = RefreshToken.ofForAdmin(admin, rawToken, LocalDateTime.now(), refreshExpirationMs);
    return repo.save(rt);
  }
}
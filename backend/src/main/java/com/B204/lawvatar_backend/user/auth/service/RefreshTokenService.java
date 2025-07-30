package com.B204.lawvatar_backend.user.auth.service;

import com.B204.lawvatar_backend.user.auth.entity.RefreshToken;
import com.B204.lawvatar_backend.user.auth.repository.RefreshTokenRepository;
import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import jakarta.transaction.Transactional;
import java.time.LocalDateTime;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class RefreshTokenService {
  private final RefreshTokenRepository repo;

  @Transactional
  public RefreshToken createForClient(Client client, String rawToken) {
    // 기존 토큰 전부 삭제
    repo.deleteByClient(client);
    // 새 토큰 저장
    RefreshToken rt = RefreshToken.ofForClient(client, rawToken, LocalDateTime.now());
    return repo.save(rt);
  }

  @Transactional
  public RefreshToken createForLawyer(Lawyer lawyer, String rawToken) {
    // 기존 토큰 전부 삭제
    repo.deleteByLawyer(lawyer);
    // 새 토큰 저장
    RefreshToken rt = RefreshToken.ofForLawyer(lawyer, rawToken, LocalDateTime.now());
    return repo.save(rt);
  }
}
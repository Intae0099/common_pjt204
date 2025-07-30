package com.B204.lawvatar_backend.user.auth.repository;

import com.B204.lawvatar_backend.user.auth.entity.RefreshToken;
import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Long> {
  Optional<RefreshToken> findByRefreshToken(String tokenHash);

  void deleteByClient(Client client);

  void deleteByLawyer(Lawyer lawyer);}

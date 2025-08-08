package com.B204.ALaw.user.auth.repository;

import com.B204.ALaw.user.admin.entity.Admin;
import com.B204.ALaw.user.auth.entity.RefreshToken;
import com.B204.ALaw.user.client.entity.Client;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import jakarta.transaction.Transactional;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Long> {
  Optional<RefreshToken> findByRefreshToken(String tokenHash);

  void deleteByClient(Client client);

  void deleteByLawyer(Lawyer lawyer);

  void deleteByAdmin(Admin admin);

  @Modifying
  @Query("DELETE FROM RefreshToken rt WHERE rt.lawyer.id = :lawyerId")
  void deleteByLawyerId(@Param("lawyerId") Long lawyerId);

  @Modifying @Transactional
  @Query("DELETE FROM RefreshToken rt WHERE rt.client.id = :clientId")
  void deleteByClientId(@Param("clientId") Long clientId);

  @Modifying @Transactional
  @Query("DELETE FROM RefreshToken rt WHERE rt.admin.id = :adminId")
  void deleteByAdminId(@Param("adminId") Long adminId);
}

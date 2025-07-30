package com.B204.lawvatar_backend.user.lawyer.repository;

import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LawyerRepository extends JpaRepository<Lawyer, Long> {
  Optional<Lawyer> findByLoginEmail(String loginEmail);
  boolean existsByLoginEmail(String loginEmail);
}

package com.B204.lawvatar_backend.user.admin.repository;

import com.B204.lawvatar_backend.user.admin.entity.Admin;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AdminRepository extends JpaRepository<Admin, Long> {
  Optional<Admin> findByLoginEmail(String loginEmail);
  boolean existsByLoginEmail(String loginEmail);
}

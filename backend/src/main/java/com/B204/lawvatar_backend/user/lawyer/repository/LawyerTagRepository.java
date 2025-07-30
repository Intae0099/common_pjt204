package com.B204.lawvatar_backend.user.lawyer.repository;

import com.B204.lawvatar_backend.user.lawyer.entity.LawyerTag;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LawyerTagRepository extends JpaRepository<LawyerTag, Long> {
}
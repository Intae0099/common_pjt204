package com.B204.ALaw.user.lawyer.repository;

import com.B204.ALaw.user.lawyer.entity.LawyerTag;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface LawyerTagRepository extends JpaRepository<LawyerTag, Long> {
  @Modifying
  @Query("DELETE FROM LawyerTag lt WHERE lt.lawyer.id = :lawyerId")
  void deleteByLawyerId(@Param("lawyerId") Long lawyerId);
}
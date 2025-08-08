package com.B204.ALaw.user.lawyer.repository;

import com.B204.ALaw.user.lawyer.entity.UnavailabilitySlot;
import java.time.LocalDateTime;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.transaction.annotation.Transactional;

public interface UnavailabilitySlotRepository extends JpaRepository<UnavailabilitySlot, Long> {
  List<UnavailabilitySlot> findByLawyerId(Long lawyerId);

  @Transactional
  void deleteByLawyerIdAndStartTimeAndEndTime(Long lawyerId, LocalDateTime start, LocalDateTime end);
}

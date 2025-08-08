package com.B204.ALaw.user.lawyer.service;

import com.B204.ALaw.user.lawyer.dto.UnavailabilitySlotDto;
import com.B204.ALaw.user.lawyer.entity.UnavailabilitySlot;
import com.B204.ALaw.user.lawyer.repository.UnavailabilitySlotRepository;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UnavailabilityService {
  private final UnavailabilitySlotRepository repo;

  public List<UnavailabilitySlotDto> getSlotsForLawyer(Long lawyerId) {
    List<UnavailabilitySlot> slots = repo.findByLawyerId(lawyerId);
    return slots.stream()
        .map(s -> new UnavailabilitySlotDto(
            s.getLawyer().getId(),
            s.getStartTime(),
            s.getEndTime()
        ))
        .collect(Collectors.toList());
  }
}

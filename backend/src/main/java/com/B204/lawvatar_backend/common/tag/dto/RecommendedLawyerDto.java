package com.B204.lawvatar_backend.common.tag.dto;

import java.util.List;
import lombok.AccessLevel;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class RecommendedLawyerDto {
  private Long lawyerId;
  private String name;
  private String introduction;
  private List<Long> tags;
}
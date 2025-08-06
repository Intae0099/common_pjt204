package com.B204.lawvatar_backend.common.tag.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RecommendLawyerRequest {
  @NotNull
  @Size(min = 1)
  private List<@NotNull Long> tagIds;

  @Min(1)
  private int limit;
}
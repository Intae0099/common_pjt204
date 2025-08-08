package com.B204.ALaw.application.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AddApplicationRequest {

    // Field
    @NotBlank(message = "[AddApplicationRequest - 001] 제목은 필수입력 값입니다.")
    private String title;

    @NotBlank(message = "[AddApplicationRequest - 002] 요약은 필수입력 값입니다.")
    private String summary;

    @NotBlank(message = "[AddApplicationRequest - 003] 본문은 필수입력 값입니다.")
    private String content;

    private String outcome;
    private String disadvantage;
    private Map<String, String> recommendedQuestion = new HashMap<>();
    private List<Long> tags;
}

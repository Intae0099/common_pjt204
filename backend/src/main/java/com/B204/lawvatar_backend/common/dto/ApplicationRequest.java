package com.B204.lawvatar_backend.common.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
/*
 * 3-3. 상담 신청서 생성
 * 요청 DTO
 */
public class ApplicationRequest {

    // Field
    @JsonProperty("case")
    private CaseDto caseDto;
    private String desiredOutcome;
    private String weakPoints;

    // Nested Class
    @Getter @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class CaseDto {

        // Field
        private String title;
        private String summary;
        private String fullText;

    }
}

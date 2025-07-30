package com.B204.lawvatar_backend.common.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
/*
 * 3-3. 상담 신청서 생성
 * 응답 DTO
 */
public class ApplicationResponse {

    // Field
    private boolean success;
    private DataDto data;
    // 태그도 이 요청에서 준다고 하셨는데 api 명세에 추가되면 dto 수정하겠습니다.

    // Nested Class
    @Getter @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class DataDto {

        // Field
        private ApplicationDto application;
        private String questions;

        // Nested Class
        @Getter @Setter
        @NoArgsConstructor
        @AllArgsConstructor
        @Builder
        public static class ApplicationDto {

            // Field
            private InnerDataDto data;
            private String weakPoints;
            private String desiredOutcome;

            // Nested Class
            @Getter @Setter
            @NoArgsConstructor
            @AllArgsConstructor
            @Builder
            public static class InnerDataDto {

                // Field
                @JsonProperty("case")
                private CaseDto caseDto;

                // Nested Class
                @Getter @Setter
                @NoArgsConstructor
                @AllArgsConstructor
                @Builder
                public static class CaseDto {

                    private String title;
                    private String summary;
                    private String fullText;

                }
            }
        }
    }
}

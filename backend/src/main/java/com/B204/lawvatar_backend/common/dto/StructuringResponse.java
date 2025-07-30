package com.B204.lawvatar_backend.common.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class StructuringResponse {

    // Field
    private boolean success;
    private DataDto data;

    // Nested Class
    @Getter @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class DataDto {

        // Field
        @JsonProperty("case")
        private CaseDto caseDto;

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
}

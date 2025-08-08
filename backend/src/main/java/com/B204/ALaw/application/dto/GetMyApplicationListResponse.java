package com.B204.ALaw.application.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GetMyApplicationListResponse {

    // Field
    private boolean success;
    private String message;
    private Data data;

    // Nested Class
    @Getter @Setter
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class Data {

        // Field
        private List<ApplicationDto> applicationList = new ArrayList<>();

        // Nested Class
        @Getter @Setter
        @NoArgsConstructor
        @AllArgsConstructor
        @Builder
        public static class ApplicationDto {

            // Field
            private Long applicationId;
            private Long clientId;
            private String title;
            private String summary;
            private String content;
            private String outcome;
            private String disadvantage;
            private Map<String, String> recommendedQuestions = new HashMap<>();
            private boolean isCompleted;
            private LocalDateTime createdAt;
            private List<Long> tags;
        }
    }
}

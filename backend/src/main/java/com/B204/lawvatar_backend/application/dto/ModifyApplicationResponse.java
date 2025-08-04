package com.B204.lawvatar_backend.application.dto;

import lombok.*;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ModifyApplicationResponse {

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
        private Long applicationId;
    }
}

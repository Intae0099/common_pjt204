package com.B204.lawvatar_backend.application.dto;

import lombok.*;

@Getter
@NoArgsConstructor
public class AddApplicationResponse {
    private Long applicationId;

    @Builder
    public AddApplicationResponse(Long applicationId) {
        this.applicationId = applicationId;
    }
}
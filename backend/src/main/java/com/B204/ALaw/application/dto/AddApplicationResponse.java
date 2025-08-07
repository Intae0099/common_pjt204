package com.B204.ALaw.application.dto;

import lombok.*;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AddApplicationResponse {

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

//    클래스 선언부에 @Builder 붙이는 것으로 대체하였습니다!
//    @Builder
//    public AddApplicationResponse(Long applicationId) {
//        this.applicationId = applicationId;
//    }

}
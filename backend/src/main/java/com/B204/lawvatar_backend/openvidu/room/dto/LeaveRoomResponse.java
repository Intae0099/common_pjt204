package com.B204.lawvatar_backend.openvidu.room.dto;

import lombok.*;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LeaveRoomResponse {

    // Field
    private boolean success;
    private String message;
    private Data data;

    // Nested Class
    public static class Data {
    }
}

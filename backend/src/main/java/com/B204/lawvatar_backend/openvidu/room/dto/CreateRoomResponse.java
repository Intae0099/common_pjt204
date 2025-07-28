package com.B204.lawvatar_backend.openvidu.room.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
public class CreateRoomResponse {

    // Field
    private Long id;
    private String customSessionId;
    private String token;

}

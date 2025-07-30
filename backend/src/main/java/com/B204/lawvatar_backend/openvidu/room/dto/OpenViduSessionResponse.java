package com.B204.lawvatar_backend.openvidu.room.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
public class OpenViduSessionResponse {

    // Field
    private String id; // openVidu 서버 내부 sessionId (customSessionId와 다른 것)

}

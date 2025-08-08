package com.B204.ALaw.openvidu.room.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
public class OpenViduConnectionResponse {

    // Field
    private String token; // 세션 입장권 (참여자마다 다른 값이 부여됨)

}

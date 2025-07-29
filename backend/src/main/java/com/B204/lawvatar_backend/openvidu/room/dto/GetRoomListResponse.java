package com.B204.lawvatar_backend.openvidu.room.dto;

import com.B204.lawvatar_backend.openvidu.room.entity.Room;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
public class GetRoomListResponse {

    // Field
    private List<Room> roomList = new ArrayList<>();

}

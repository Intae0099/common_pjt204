package com.B204.lawvatar_backend.openvidu.room.repository;

import com.B204.lawvatar_backend.openvidu.room.entity.Room;
import jakarta.persistence.EntityManager;
import lombok.RequiredArgsConstructor;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

public interface RoomRepository extends JpaRepository<Room, Long> {

}
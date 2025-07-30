package com.B204.lawvatar_backend.openvidu.room.repository;

import com.B204.lawvatar_backend.openvidu.room.entity.Room;
import jakarta.persistence.EntityManager;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
@RequiredArgsConstructor
public class RoomRepository {

    // Field
    private final EntityManager em;

    // Method
    public Long save(Room room) {
        em.persist(room);
        return room.getId();
    }

    public List<Room> findByCustomSessionId(String customSessionId) {
        return em.createQuery("select r from Room r where openviduCustomSessionId=:customSessionId", Room.class)
                .setParameter("customSessionId", customSessionId)
                .getResultList();
    }

    public List<Room> findAll() {
        return em.createQuery("select r from Room r", Room.class).getResultList();
    }
}
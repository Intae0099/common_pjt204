package com.B204.lawvatar_backend.openvidu.participant.repository;

import com.B204.lawvatar_backend.openvidu.participant.entity.Participant;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ParticipantRepository extends JpaRepository<Participant, Long> {
}

package com.B204.ALaw.openvidu.participant.repository;

import com.B204.ALaw.openvidu.participant.entity.Participant;
import com.B204.ALaw.openvidu.room.entity.Room;
import com.B204.ALaw.user.client.entity.Client;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ParticipantRepository extends JpaRepository<Participant, Long> {
    void deleteByClientId(Long userId);
    void deleteByLawyerId(Long lawyerId);
    Participant findByClient(Client client);
    Participant findByLawyer(Lawyer lawyer);
    Participant findByRoom(Room room);
    Participant findByClientId(Long userId);
    Participant findByLawyerId(Long userId);
}

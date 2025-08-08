package com.B204.ALaw.user.lawyer.entity;

import com.B204.ALaw.appointment.entity.Appointment;
import com.B204.ALaw.openvidu.participant.entity.Participant;
import com.B204.ALaw.user.auth.entity.RefreshToken;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Entity
@Data
@NoArgsConstructor
public class Lawyer {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(columnDefinition = "int unsigned")
    private Long id;

    @Column(name = "login_email", nullable = false, unique = true, length = 100)
    private String loginEmail;

    @Column(name = "login_password_hash", nullable = false, length = 255)
    private String passwordHash;

    @Lob
    @Column(name = "photo", columnDefinition = "longblob")
    private byte[] photo;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(columnDefinition = "text")
    private String introduction;

    @Column(length = 100, nullable = false)
    private String exam;

    @Column(length = 100, nullable = false)
    private String registrationNumber;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, columnDefinition = "varchar(100) default 'PENDING'")
    private CertificationStatus certificationStatus = CertificationStatus.PENDING;

    @Column(columnDefinition = "int unsigned default 0", nullable = false)
    private int consultationCount = 0;

    @OneToMany(mappedBy = "lawyer", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<RefreshToken> refreshTokenList = new ArrayList<>();

    @OneToMany(mappedBy = "lawyer", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<LawyerTag> tags = new ArrayList<>();

    @OneToMany(mappedBy = "lawyer", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<Appointment> appointmentList = new ArrayList<>();

    @OneToMany(mappedBy = "lawyer", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<UnavailabilitySlot> unavailabilitySlotList = new ArrayList<>();

    @OneToOne(mappedBy = "lawyer", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private Participant participant;

}

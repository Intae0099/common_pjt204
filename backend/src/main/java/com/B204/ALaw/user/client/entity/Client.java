package com.B204.ALaw.user.client.entity;

import com.B204.ALaw.application.entity.Application;
import com.B204.ALaw.appointment.entity.Appointment;
import com.B204.ALaw.openvidu.participant.entity.Participant;
import com.B204.ALaw.user.auth.entity.RefreshToken;
import jakarta.persistence.*;
import lombok.*;

import java.util.ArrayList;
import java.util.List;

@Entity
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Client {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(columnDefinition = "int unsigned")
    private Long id;

    @Column(length = 100, nullable = false)
    private String oauthName;

    @Column(length = 100, unique = true)
    private String email;

    @Column(length = 100, nullable = false)
    private String oauthProvider;

    @Column(length = 100, nullable = false)
    private String oauthIdentifier;

    @OneToMany(mappedBy = "client", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<RefreshToken> refreshTokenList = new ArrayList<>();

    @OneToMany(mappedBy = "client", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<Application> applicationList = new ArrayList<>();

    @OneToMany(mappedBy = "client", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<Appointment> appointmentList = new ArrayList<>();

    @OneToOne(mappedBy = "client", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private Participant participant;

    // Constructor
    public Client(String oauthName, String oauthProvider){
        this.oauthName = oauthName;
        this.oauthProvider = oauthProvider;
    }

    public Client(String oauthIdentifier, String oauthName, String oauthProvider){
        this.oauthIdentifier = oauthIdentifier;
        this.oauthName = oauthName;
        this.oauthProvider = oauthProvider;
    }

}

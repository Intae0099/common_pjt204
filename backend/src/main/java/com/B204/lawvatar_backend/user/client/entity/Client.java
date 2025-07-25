package com.B204.lawvatar_backend.user.client.entity;

import jakarta.annotation.Nullable;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class Client {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "client_id")
    private Long id;

    @Column(length = 20)
    private String oauthName;

    @Column(length = 30)
    private String email;

    @Column(length = 20)
    private String oauthProvider;

    @Column(length = 20)
    private String oauthIdentifier;

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

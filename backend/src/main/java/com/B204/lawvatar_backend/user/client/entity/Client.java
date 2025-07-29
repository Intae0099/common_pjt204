package com.B204.lawvatar_backend.user.client.entity;

import jakarta.annotation.Nullable;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Client {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 20, nullable = false)
    private String oauthName;

    @Column(length = 100, unique = true)
    private String email;

    @Column(length = 20, nullable = false)
    private String oauthProvider;

    @Column(length = 100, nullable = false)
    private String oauthIdentifier;

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

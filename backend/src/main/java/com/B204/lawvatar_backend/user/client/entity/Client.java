package com.B204.lawvatar_backend.user.client.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Getter
@NoArgsConstructor
public class Client {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "client_id")
    private Long id;

    @Column(length = 20)
    private String name;

    @Column(length = 30)
    private String email;

    @Column(length = 20)
    private String oauthProvider;

    @Column(length = 30)
    private String oauthIdentifier;

}

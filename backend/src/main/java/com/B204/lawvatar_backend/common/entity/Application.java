package com.B204.lawvatar_backend.common.entity;

import jakarta.persistence.*;

@Entity
public class Application {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "client_id")
    private Client client;

    @Column(length = 60000)
    // 60000byte = 워드 한국어로 10-12페이지 정도 분량
    private String summary;

    @Column(length = 60000)
    private String outcome;

    @Column(length = 60000)
    private String disadvantage;

}

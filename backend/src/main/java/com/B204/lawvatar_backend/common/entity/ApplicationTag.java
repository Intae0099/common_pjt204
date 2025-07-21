package com.B204.lawvatar_backend.common.entity;

import jakarta.persistence.*;

@Entity
public class ApplicationTag {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "tag_id") // 여기가 외래키의 위치
    private Tag tag;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "application_id")
    private Application application;
}

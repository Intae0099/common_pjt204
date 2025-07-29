package com.B204.lawvatar_backend.user.lawyer.entity;

import com.B204.lawvatar_backend.common.entity.Tag;
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
    private Long id;

    @Column(name = "login_email", nullable = false, unique = true, length = 100)
    private String loginEmail;

    @Column(name = "login_password_hash", nullable = false, length = 255)
    private String loginPasswordHash;

    @Column(columnDefinition = "text")
    private String photo;

    @Column(length = 20, nullable = false)
    private String name;

    @Column(columnDefinition = "TEXT")
    private String introduction;

    @Column(length = 20, nullable = false)
    private String exam;

    @Column(length = 20, nullable = false)
    private String registrationNumber;

    @Enumerated(EnumType.STRING)
    private CertificationStatus certificationStatus = CertificationStatus.PENDING;

    @Column(columnDefinition = "int unsigned", nullable = false)
    private int consultationCount = 0;

    @OneToMany(mappedBy = "lawyer", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<LawyerTag> tags = new ArrayList<>();

}

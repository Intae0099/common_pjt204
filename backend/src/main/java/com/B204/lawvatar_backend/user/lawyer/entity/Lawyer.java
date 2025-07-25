package com.B204.lawvatar_backend.user.lawyer.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

@Entity
@Getter
@NoArgsConstructor
public class Lawyer {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 20)
    private String loginId;

    @Column(length = 30)
    private String loginPwd;

    private String name;
    private String email;

    @Column(columnDefinition = "text")
    private String introduction;

    @Column(columnDefinition = "int unsigned")
    private int consultationCount;

    @Enumerated(EnumType.STRING)
    private CertificationStatus certificationStatus;

    @OneToMany(mappedBy = "lawyer")
    List<LawyerTag> tagList = new ArrayList<>();

}

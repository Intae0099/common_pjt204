package com.B204.lawvatar_backend.common.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

@Entity
@Getter @Setter
@NoArgsConstructor
public class Lawyer {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 20) // PM/UX에 따라 길이제한은 달라질 수 있음
    private String loginId;

    @Column(length = 30) // PM/UX에 따라 길이제한은 달라질 수 있음
    private String loginPwd;

    private String name;

    private String email;

    @Column(length = 500)
    private String introduction;

    @Column(columnDefinition = "int unsigned")
    private int consultationCount;

    @Enumerated(EnumType.STRING)
    private CertificationStatus certificationStatus;

    @OneToMany(mappedBy = "lawyer")
    List<LawyerTag> tagList = new ArrayList<>();

}

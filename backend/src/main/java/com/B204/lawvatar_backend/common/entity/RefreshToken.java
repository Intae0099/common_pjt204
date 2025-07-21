package com.B204.lawvatar_backend.common.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Getter @Setter
public class RefreshToken {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 리프레시 토큰의 소유자 (의뢰인 또는 변호사)
    private Client client;
    private Lawyer lawyer;

    @Column(length = 1024)
    // JWT는 보통 200~500자 정도이므로, JWT를 저장할 컬럼의 길이를 512 or 1024 바이트로 두는 것이 일반적. (2의 배수로 두는 것이 관례)
    private String refreshToken;

    // 리프레시 토큰 발급시각
    private LocalDateTime issuedAt;

    // 리프레시 토큰 폐기시각
    private LocalDateTime revokedAt;
    
}

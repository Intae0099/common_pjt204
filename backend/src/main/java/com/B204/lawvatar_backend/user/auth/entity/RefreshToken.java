package com.B204.lawvatar_backend.user.auth.entity;

import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor
public class RefreshToken {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "refresh_token_id")
    private Long id;

    // 리프레시 토큰의 소유자 (의뢰인 또는 변호사)
    // nullable로 해야함ㅠㅠ
    private Client client;
    private Lawyer lawyer;

    @Column(length = 1024)
    // JWT는 보통 200~500자 정도이므로, JWT를 저장할 컬럼의 길이를 512 or 1024 바이트로 두는 것이 일반적. (2의 배수로 두는 것이 관례)
    private String refreshToken;

    private LocalDateTime issuedAt;
    private LocalDateTime revokedAt;
    
}

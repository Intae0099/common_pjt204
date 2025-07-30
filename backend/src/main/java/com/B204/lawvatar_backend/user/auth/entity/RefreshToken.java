package com.B204.lawvatar_backend.user.auth.entity;

import com.B204.lawvatar_backend.user.client.entity.Client;
import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.extern.apachecommons.CommonsLog;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor
public class RefreshToken {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 리프레시 토큰의 소유자 (의뢰인 또는 변호사)
    // nullable로 해야함ㅠㅠ
<<<<<<< HEAD
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "client_id")
    private Client client;

    @OneToOne(fetch = FetchType.LAZY)
=======
    // 의뢰인용 foreign key
    @ManyToOne(fetch = FetchType.LAZY, optional = true)
    @JoinColumn(name = "client_id")
    private Client client;

    // 변호사용 foreign key
    @ManyToOne(fetch = FetchType.LAZY, optional = true)
>>>>>>> d6e43e84b49ca078725d21a605311f95920e18fc
    @JoinColumn(name = "lawyer_id")
    private Lawyer lawyer;

    @Column(name = "refresh_token", length = 1024, nullable = false)
    // JWT는 보통 200~500자 정도이므로, JWT를 저장할 컬럼의 길이를 512 or 1024 바이트로 두는 것이 일반적. (2의 배수로 두는 것이 관례)
    private String refreshToken;

    @Column(name = "issued_at", nullable = false)
    private LocalDateTime issuedAt;

    @Column(name = "revoked_at")
    private LocalDateTime revokedAt;

    // 생성자 및 편의 메서드
    public static RefreshToken ofForClient(Client client, String token, LocalDateTime issuedAt) {
        RefreshToken rt = new RefreshToken();
        rt.client = client;
        rt.refreshToken = token;
        rt.issuedAt = issuedAt;
        return rt;
    }

    public static RefreshToken ofForLawyer(Lawyer lawyer, String token, LocalDateTime issuedAt) {
        RefreshToken rt = new RefreshToken();
        rt.lawyer = lawyer;
        rt.refreshToken = token;
        rt.issuedAt = issuedAt;
        return rt;
    }

    public void revoke(LocalDateTime when) {
        this.revokedAt = when;
    }
}

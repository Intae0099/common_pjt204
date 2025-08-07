package com.B204.ALaw.user.auth.entity;

import com.B204.ALaw.user.admin.entity.Admin;
import com.B204.ALaw.user.client.entity.Client;
import com.B204.ALaw.user.lawyer.entity.Lawyer;
import jakarta.persistence.*;
import java.time.Duration;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor
public class RefreshToken {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(columnDefinition = "int unsigned")
    private Long id;

    // 리프레시 토큰의 소유자 (의뢰인/변호사/관리자)
    // 의뢰인용 foreign key
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "client_id") // optional = true는 기본값이라서 뺐습니다!
    private Client client;

    // 변호사용 foreign key
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "lawyer_id")
    private Lawyer lawyer;

    // 관리자용 foreign key
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "admin_id")
    private Admin admin;

    @Column(length = 1024, nullable = false)
    // JWT는 보통 200~500자 정도이므로, JWT를 저장할 컬럼의 길이를 512 or 1024 바이트로 두는 것이 일반적. (2의 배수로 두는 것이 관례)
    private String refreshToken;

    @Column(nullable = false)
    private LocalDateTime issuedAt;

    private LocalDateTime revokedAt;

    // 생성자 및 편의 메서드
    public static RefreshToken ofForClient(
            Client client,
            String token,
            LocalDateTime issuedAt,
            long refreshExpirationMs) {

        RefreshToken rt = new RefreshToken();
        rt.client = client;
        rt.refreshToken = token;
        rt.issuedAt = issuedAt;
        rt.revokedAt = issuedAt.plus(Duration.ofMillis(refreshExpirationMs));
        return rt;
    }

    public static RefreshToken ofForLawyer(
            Lawyer lawyer,
            String token,
            LocalDateTime issuedAt,
            long refreshExpirationMs) {
        RefreshToken rt = new RefreshToken();
        rt.lawyer = lawyer;
        rt.refreshToken = token;
        rt.issuedAt = issuedAt;
        rt.revokedAt = issuedAt.plus(Duration.ofMillis(refreshExpirationMs));
        return rt;
    }

    public static RefreshToken ofForAdmin(
            Admin admin,
            String token,
            LocalDateTime issuedAt,
            long refreshExpirationMs) {
        RefreshToken rt = new RefreshToken();
        rt.admin = admin;
        rt.refreshToken = token;
        rt.issuedAt = issuedAt;
        rt.revokedAt = issuedAt.plus(Duration.ofMillis(refreshExpirationMs));
        return rt;
    }
}

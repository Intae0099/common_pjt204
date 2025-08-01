package com.B204.lawvatar_backend.application.entity;

import com.B204.lawvatar_backend.user.client.entity.Client;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.Fetch;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Entity
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Application {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "client_id", nullable = false)
    private Client client;

    /*사건 경위서*/
    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String summary;

    @Column(columnDefinition = "text", nullable = false)
    private String content;

    /*상담신청서 남은 문항*/
    @Column(columnDefinition = "text")
    private String outcome;

    @Column(columnDefinition = "text")
    private String disadvantage;

    // 통 JSON으로 그대로 넘어올 예정
    @Column(columnDefinition = "json")
    @JdbcTypeCode(SqlTypes.JSON)
    private Map<String, String> recommendedQuestion = new HashMap<>();

    @Column(nullable = false)
    private boolean isCompleted;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    // ApplicationTag 테이블에서 applicationId가 이 applicationId와 같은 것들 조회해서 리스트로 가지고 있기
    @OneToMany(mappedBy = "application", fetch = FetchType.LAZY)
    private List<ApplicationTag> tags = new ArrayList<>();

}

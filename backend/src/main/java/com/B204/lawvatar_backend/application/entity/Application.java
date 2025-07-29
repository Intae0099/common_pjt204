package com.B204.lawvatar_backend.application.entity;

import com.B204.lawvatar_backend.user.client.entity.Client;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor
public class Application {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "client_id")
    @Column(nullable = false)
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

    /*AI가 생성해주는 추천질문*/
    // JSON으로 그대로 넘어올 예정
    @Column(columnDefinition = "json")
    private String recommendedQuestion;

    @Column(nullable = false)
    private boolean isCompleted;

    @Column(nullable = false)
    private LocalDateTime createdAt;

}

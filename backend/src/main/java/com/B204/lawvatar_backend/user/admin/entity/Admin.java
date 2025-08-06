package com.B204.lawvatar_backend.user.admin.entity;

import com.B204.lawvatar_backend.user.auth.entity.RefreshToken;
import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Entity
@Data
@Table(name = "admin")
@NoArgsConstructor
public class Admin {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  @Column(columnDefinition = "int unsigned")
  private Long id;

  @Column(name = "login_email", nullable = false, unique = true, length = 100)
  private String loginEmail;

  @Column(name = "login_password_hash", nullable = false, length = 255)
  private String loginPasswordHash;

  @Column(name = "name", nullable = false, length = 20)
  private String name;

  @OneToMany(mappedBy = "admin", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
  private List<RefreshToken> refreshTokenList = new ArrayList<>();

}

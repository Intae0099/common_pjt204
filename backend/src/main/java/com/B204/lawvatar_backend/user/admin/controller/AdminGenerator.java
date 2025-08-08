package com.B204.lawvatar_backend.user.admin.controller;

import java.time.LocalDateTime;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class AdminGenerator {

  public static void main(String[] args) {
    BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
    String rawPassword = "admin"; // 원본 비밀번호
    String hashedPassword = encoder.encode(rawPassword);

    System.out.println("bcrypt hash: " + hashedPassword);
  }
}

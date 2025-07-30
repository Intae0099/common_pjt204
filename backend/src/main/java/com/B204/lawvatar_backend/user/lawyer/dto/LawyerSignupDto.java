package com.B204.lawvatar_backend.user.lawyer.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.ArrayList;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor       // 기본 생성자
@AllArgsConstructor      // 모든 필드를 인자로 받는 생성자 (선택)
public class LawyerSignupDto {

    private String loginEmail;        // 로그인 이메일
    private String password;     // 비밀번호 (평문 입력, 서버에서 암호화)
    private String name;         // 변호사 이름
    private String introduction;
    private String exam;
    private String registrationNumber;
    private String photoBase64;

    private ArrayList<Long> tags;
}

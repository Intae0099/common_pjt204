package com.B204.lawvatar_backend.user.lawyer.dto;

import java.util.ArrayList;
import lombok.Data;

@Data
public class LawyerSignupDto {

    private String loginEmail;        // 로그인 이메일
    private String password;     // 비밀번호 (평문 입력, 서버에서 암호화)
    private String name;         // 변호사 이름
    private String introduction;
    private String exam;
    private String registrationNumber;

    private ArrayList<Long> tags;
}

package com.B204.lawvatar_backend.common.tag.entity;

import com.B204.lawvatar_backend.user.lawyer.entity.Lawyer;
import com.B204.lawvatar_backend.user.lawyer.entity.LawyerTag;
import jakarta.persistence.*;
import lombok.Data;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

@Entity
@Data
@NoArgsConstructor
public class Tag {

    // Field
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long Id;

    private String name;
    
    // Tag가 자기자신을 태그로 가지는 Lawyer 목록을 알 필요가 없을 거 같아서 lawyers 필드 삭제

}

package com.B204.lawvatar_backend.application.repository;

import com.B204.lawvatar_backend.application.entity.ApplicationTag;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ApplicationTagRepository extends JpaRepository<ApplicationTag, Long> {

    // Abstract Method
    List<ApplicationTag> findByApplicationId(Long applicationId);
}

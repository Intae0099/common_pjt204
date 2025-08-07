package com.B204.ALaw.application.repository;

import com.B204.ALaw.application.entity.ApplicationTag;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ApplicationTagRepository extends JpaRepository<ApplicationTag, Long> {

    // Abstract Method
    List<ApplicationTag> findByApplicationId(Long applicationId);
}

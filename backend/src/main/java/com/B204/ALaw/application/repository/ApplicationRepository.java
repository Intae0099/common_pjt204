package com.B204.ALaw.application.repository;

import com.B204.ALaw.application.entity.Application;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ApplicationRepository extends JpaRepository<Application, Long> {

    // Method
    List<Application> findByClientId(Long clientId);

    List<Application> findByClientIdAndIsCompletedTrue(Long clientId);

    List<Application> findByClientIdAndIsCompletedFalse(Long clientId);

    Optional<Application> findById(Long applicationId);
}

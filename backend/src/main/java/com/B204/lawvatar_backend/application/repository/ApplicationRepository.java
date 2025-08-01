package com.B204.lawvatar_backend.application.repository;

import com.B204.lawvatar_backend.application.entity.Application;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

public interface ApplicationRepository extends JpaRepository<Application, Long> {

    // Method
    List<Application> findByClientId(Long clientId);

    List<Application> findByClientIdAndIsCompletedTrue(Long clientId);

    List<Application> findByClientIdAndIsCompletedFalse(Long clientId);

    Optional<Application> findById(Long applicationId);
}

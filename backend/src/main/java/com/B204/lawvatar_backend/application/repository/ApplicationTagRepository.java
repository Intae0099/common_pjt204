package com.B204.lawvatar_backend.application.repository;

import com.B204.lawvatar_backend.application.entity.Application;
import com.B204.lawvatar_backend.application.entity.ApplicationTag;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ApplicationTagRepository extends JpaRepository<ApplicationTag, Long> {
    List<Application> findByApplicationId(List<Application> applicationList);
}

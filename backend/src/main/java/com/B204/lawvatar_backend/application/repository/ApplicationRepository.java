package com.B204.lawvatar_backend.application.repository;

import com.B204.lawvatar_backend.application.entity.Application;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ApplicationRepository extends JpaRepository<Application, Long> {

}

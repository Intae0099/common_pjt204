package com.B204.ALaw.user.client.repository;

import com.B204.ALaw.user.client.entity.Client;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ClientRepository extends JpaRepository<Client, Long> {
  Optional<Client> findByOauthIdentifier(String kakaoId);
}

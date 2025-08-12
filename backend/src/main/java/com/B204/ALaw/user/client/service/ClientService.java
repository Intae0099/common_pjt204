package com.B204.ALaw.user.client.service;

import com.B204.ALaw.user.auth.repository.RefreshTokenRepository;
import com.B204.ALaw.user.client.dto.ClientUpdateDto;
import com.B204.ALaw.user.client.entity.Client;
import com.B204.ALaw.user.client.repository.ClientRepository;
import jakarta.persistence.EntityNotFoundException;
import jakarta.transaction.Transactional;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserService;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.OAuth2Error;
import org.springframework.security.oauth2.core.user.DefaultOAuth2User;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;

@Service
public class ClientService implements OAuth2UserService<OAuth2UserRequest, OAuth2User> {

  private static final Logger log = LoggerFactory.getLogger(ClientService.class);
  private final ClientRepository clientRepo;
  private final RefreshTokenRepository refreshTokenRepo;

  public ClientService(ClientRepository clientRepo,
      RefreshTokenRepository refreshTokenRepo) {
    this.clientRepo = clientRepo;
    this.refreshTokenRepo = refreshTokenRepo;
  }

  @Override
  public OAuth2User loadUser(OAuth2UserRequest req) throws OAuth2AuthenticationException {
    // 1) 실제 카카오가 내려준 속성 전체와 userNameAttributeName(id 키)를 로깅
    OAuth2User oauth = new DefaultOAuth2UserService().loadUser(req);
    String userNameAttr = req.getClientRegistration()
        .getProviderDetails()
        .getUserInfoEndpoint()
        .getUserNameAttributeName();
    log.debug("Kakao user attributes: {}", oauth.getAttributes());
    Object rawId = oauth.getAttribute(userNameAttr);
    log.debug("Resolved userNameAttributeName '{}' = {}", userNameAttr, rawId);

    // 1) Null-safe 체크: id가 없으면 예외
    if (rawId == null) {
      throw new OAuth2AuthenticationException(
          new OAuth2Error("invalid_user_info", "Kakao ID is null", null),
          "Kakao에서 사용자 ID(id) 정보를 가져올 수 없습니다."
      );
    }

    // 2) Long 변환
    @SuppressWarnings("unchecked")
    Map<String,Object> kakaoAccount = oauth.getAttribute("kakao_account");
    Map<String,Object> profile      = (Map<String,Object>) kakaoAccount.get("profile");
    String nickname                = (String) profile.get("nickname");

    // 3) 기존 사용자 조회, 없으면 생성
    Client client = clientRepo.findByOauthIdentifier(rawId.toString())
        .orElseGet(() -> clientRepo.save(new Client(rawId.toString(), nickname, "kakao")));

    // 4) 스프링 시큐리티용 OAuth2User 반환
    return new DefaultOAuth2User(
        List.of(() -> "ROLE_CLIENT"),
        oauth.getAttributes(),
        userNameAttr  // "id"
    );
  }

  @Transactional
  public void updateClientInfo(Long clientId, ClientUpdateDto dto) {
    Client client = clientRepo.findById(clientId)
        .orElseThrow(() -> new EntityNotFoundException("Client not found"));

    if (dto.getOauthName() != null) {
      client.setOauthName(dto.getOauthName());
    }
    if (dto.getEmail() != null) {
      client.setEmail(dto.getEmail());
    }
  }

  public void deleteByClientId(Long id) {

    // ##### appointment & booking Repo 개발 후 추가
    // 1) 상담신청서 삭제
    // applicationRepo.deleteByClientId(clientId);

    // 2) 예약 내역 삭제
    // bookingRepo.deleteByClientId(clientId);

    refreshTokenRepo.deleteByClientId(id);
    clientRepo.deleteById(id);

  }
}
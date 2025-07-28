package com.B204.lawvatar_backend.user.client.controller;


import com.B204.lawvatar_backend.common.principal.ClientPrincipal;
import com.B204.lawvatar_backend.common.util.JwtUtil;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/clients")
public class ClientController {

  @GetMapping("/me")
  public ResponseEntity<Map<String, Object>> getMyInfo(Authentication authentication){
    Object principal = authentication.getPrincipal();

    if(!(principal instanceof ClientPrincipal client)){
      return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of(
          "error", "의뢰인으로서 권한이 없습니다."
      ));
    }

    Map<String ,Object> response = new LinkedHashMap<>();
    response.put("clientId", client.getUsername());
    response.put("oauthName", client.getOauthtName());
    response.put("oauthProvider", client.getOauthProvider());
    response.put("oauthIdentifier", client.getOauthIndentifier());

    return ResponseEntity.ok(response);
  }

}

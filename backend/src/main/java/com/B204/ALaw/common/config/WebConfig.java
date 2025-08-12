package com.B204.ALaw.common.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.servers.Server;
import java.util.List;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

  // Method
  /**
   * AI 파트에 요청보낼 때 필요해서 빈주입 메서드 추가
   * @return RestTemplate 객체
   */
  @Bean
  public RestTemplate restTemplate() {
    return new RestTemplate();
  }

  @Bean
  public OpenAPI openAPI() {
    return new OpenAPI().servers(List.of(new Server().url("/")));
  }

  @Override
  public void addCorsMappings(CorsRegistry registry) {
    registry.addMapping("/**")
        .allowedOrigins("http://localhost:5173", "https://i13b204.p.ssafy.io", "http://192.168.31.252", "http://14.50.47.252")
        .allowedMethods("GET","POST", "PATCH" ,"PUT","DELETE","OPTIONS")
        .allowedHeaders("*")
        .allowCredentials(true);
  }

}

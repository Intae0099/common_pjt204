# --- 1. Build Stage ---
# Maven과 JDK가 포함된 이미지를 빌드 환경으로 사용합니다.
FROM maven:3-eclipse-temurin-21 AS builder

# 작업 디렉토리 설정
WORKDIR /app

# pom.xml을 먼저 복사하여 의존성 레이어를 캐싱합니다.
# 소스 코드가 변경되어도 pom.xml이 변경되지 않았다면, 의존성을 다시 다운로드하지 않아 빌드 속도가 향상됩니다.
COPY pom.xml .
RUN mvn dependency:go-offline

# 나머지 소스 코드를 복사합니다.
COPY src ./src

# Maven을 사용하여 애플리케이션을 빌드합니다. 테스트는 CI 단계에서 이미 수행했다고 가정하고 스킵합니다.
RUN mvn package -DskipTests


# --- 2. Run Stage ---
# 실제 애플리케이션을 실행할 환경입니다. JRE만 있으면 되므로 더 가볍습니다.
FROM eclipse-temurin:21-jre-jammy

# 작업 디렉토리 설정
WORKDIR /app

# builder 스테이지에서 빌드된 .jar 파일을 복사합니다.
COPY --from=builder /app/target/*.jar app.jar

# 컨테이너가 시작될 때 실행할 명령어
ENTRYPOINT ["java", "-jar", "app.jar"]
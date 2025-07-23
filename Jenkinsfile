// 파이프라인 변수 설정
def springImageName = "localhost:5000/backend-app"
def vueImageName = "localhost:5000/frontend-app"

pipeline {
    agent any

    environment {
        GITLAB_REGISTRY_CREDENTIALS_ID = 'gitlab-registry-credentials'
        EC2_SSH_CREDENTIALS_ID = 'ec2-ssh-key'
    }

    stages {
        // stage('Clean Workspace') {
        //     steps {
        //         // 이전 빌드 아티팩트 정리
        //         cleanWs()
        //     }
        // }

        stage('Build Backend & Frontend') {
            // 백엔드와 프론트엔드 빌드를 병렬로 실행하여 시간 단축
            parallel {
                stage('Build Backend Image') {
                    steps {
                        echo "Building Backend Docker image..."
                        // Dockerfile에서 multi-stage build를 사용하므로 별도의 빌드 과정 불필요
                        // backend-app 이라는 이미지 이름으로 빌드
                        sh "docker build -t ${springImageName}:${env.BUILD_ID} -f backend/Dockerfile ./backend"
                    }
                }
                stage('Build Frontend Image') {
                    steps {
                        echo "Building Frontend Docker image..."
                        // frontend-app 이라는 이미지 이름으로 빌드
                        sh "docker build -t ${vueImageName}:${env.BUILD_ID} -f frontend/Dockerfile ./frontend"
                    }
                }
            }
        }

        stage('Push Docker Images to Local Registry') { // 스테이지 이름 변경 (권장)
            steps {
                // 로그인 과정 없이 바로 푸시
                sh "docker push ${springImageName}:${env.BUILD_ID}"
                sh "docker push ${vueImageName}:${env.BUILD_ID}"
            }
        }

        stage('Deploy on Local Host') { 
            steps {
            
                // Jenkins가 EC2 호스트에서 직접 스크립트를 실행합니다.
                sh """
                    echo "배포 스크립트를 직접 실행합니다..."
                    /app/deploy.sh ${env.BUILD_ID}
                """
            }
        }
    }

    post {
        always {
            script {
                
                // 빌드에 사용된 로컬 Docker 이미지 정리 (선택사항, Jenkins 서버 용량 관리)
                sh "docker rmi ${springImageName}:${env.BUILD_ID} || true"
                sh "docker rmi ${vueImageName}:${env.BUILD_ID} || true"
            }
        }
    }
}
// 파이프라인 변수 설정
def springImageName = "lab.ssafy.com/s13-webmobile1-sub1/s13p11b204/backend-app"
def vueImageName = "lab.ssafy.com/s13-webmobile1-sub1/s13p11b204/frontend-app"

pipeline {
    agent any

    environment {
        GITLAB_REGISTRY_CREDENTIALS_ID = 'gitlab-registry-credentials'
        EC2_SSH_CREDENTIALS_ID = 'ec2-ssh-key'
    }

    stages {
        stage('Clean Workspace') {
            steps {
                // 이전 빌드 아티팩트 정리
                cleanWs()
            }
        }

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

        stage('Push Docker Images to GitLab Registry') {
            steps {
                script {
                    // GitLab Registry에 로그인
                    withCredentials([usernamePassword(credentialsId: GITLAB_REGISTRY_CREDENTIALS_ID, passwordVariable: 'GITLAB_PASSWORD', usernameVariable: 'GITLAB_USERNAME')]) {
                        sh "docker login lab.ssafy.com -u ${GITLAB_USERNAME} -p ${GITLAB_PASSWORD}"
                    }

                    // 빌드된 이미지에 태그 추가 및 푸시
                    sh "docker push ${springImageName}:${env.BUILD_ID}"
                    sh "docker push ${vueImageName}:${env.BUILD_ID}"
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                // sshagent를 사용하여 EC2에 접속
                sshagent(credentials: [EC2_SSH_CREDENTIALS_ID]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ubuntu@<YOUR_EC2_PUBLIC_IP> '
                            # 배포 스크립트 실행 (전달 인자로 이미지 태그 전달)
                            /home/ubuntu/deploy.sh ${env.BUILD_ID}
                        '
                    """
                }
            }
        }
    }

    post {
        always {
            script {
                // GitLab Registry 로그아웃
                sh "docker logout lab.ssafy.com"
                
                // 빌드에 사용된 로컬 Docker 이미지 정리 (선택사항, Jenkins 서버 용량 관리)
                sh "docker rmi ${springImageName}:${env.BUILD_ID} || true"
                sh "docker rmi ${vueImageName}:${env.BUILD_ID} || true"
            }
        }
    }
}
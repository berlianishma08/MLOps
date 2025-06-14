pipeline {
    agent any

    environment {
        TIMESTAMP = "${new Date().format('yyyyMMdd_HHmmss')}"
        DOCKER_HUB_CREDENTIALS_ID = 'jen-dockerhub'
        DOCKER_HUB_REPO = 'berlianishma08/mlops'
        VENV_NAME = 'myenv'
        DOCKER_APP_NAME = 'mlops-app'
        DOCKER_TEST_NAME = 'mlops-test'
    }

    stages {
        stage('Checkout Repository') {
            steps {
                git credentialsId: 'jen-doc-git', 
                    url: 'https://github.com/berlianishma08/MLOps.git',
                    branch: 'master'  // Explicitly specify branch
            }
        }

        stage('Setup Environment') {
            steps {
                sh """
                python3 -m venv ${VENV_NAME}
                . ${VENV_NAME}/bin/activate
                pip install --upgrade pip
                pip install setuptools wheel
                """
            }
        }

        stage('Install Dependencies') {
            steps {
                sh """
                . ${VENV_NAME}/bin/activate
                pip install --upgrade pip setuptools wheel
                pip install catboost==1.2.2 --no-cache-dir
                pip install -r requirements.txt
                """
            }
        }

        stage('Run Data Preparation') {
            steps {
                sh """
                . ${VENV_NAME}/bin/activate
                python Script/data_preparation.py \
                    --data_dir Data/raw \
                    --data_new Data/clean \
                    --output_dir Model/preprocessor \
                    --target_col Survived \
                    --random_state 42 \
                    --columns_to_remove "Cabin PassengerId Name" \
                    --timestamp ${TIMESTAMP}
                """
            }
        }

        stage('Train Model') {
            steps {
                sh """
                . ${VENV_NAME}/bin/activate
                python Script/train_model.py \
                    --data_dir Data/clean \
                    --model_dir Model/model \
                    --timestamp ${TIMESTAMP} \
                    --model_name random_forest
                """
            }
        }

        stage('Deploy Model') {
            steps {
                sh """
                . ${VENV_NAME}/bin/activate
                python Script/deploy_model.py \
                    --model_path Model/model/random_forest_${TIMESTAMP}.pkl \
                    --model_dir Model/model \
                    --metadata_dir Model/metadata \
                    --timestamp ${TIMESTAMP}
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_HUB_REPO}:${TIMESTAMP}", "--no-cache .")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_HUB_CREDENTIALS_ID}") {
                        dockerImage.push("${TIMESTAMP}")
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Test Docker Image') {
            steps {
                script {
                    try {
                        // Run test container
                        sh """
                        docker stop ${DOCKER_TEST_NAME} || true
                        docker rm ${DOCKER_TEST_NAME} || true
                        docker run -d --name ${DOCKER_TEST_NAME} -p 3001:3000 ${DOCKER_HUB_REPO}:${TIMESTAMP}
                        
                        // Health check with retries
                        for i in {1..5}; do
                            curl -f http://localhost:3001/health && break || sleep 10
                        done || exit 1
                        """
                    } finally {
                        // Cleanup test container
                        sh """
                        docker stop ${DOCKER_TEST_NAME} || true
                        docker rm ${DOCKER_TEST_NAME} || true
                        """
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                sh """
                # Stop and remove old container
                docker stop ${DOCKER_APP_NAME} || true
                docker rm ${DOCKER_APP_NAME} || true
                
                # Deploy new container with resource limits
                docker run -d \
                    --name ${DOCKER_APP_NAME} \
                    -p 3000:3000 \
                    --restart unless-stopped \
                    --memory 512m \
                    --cpus 1 \
                    ${DOCKER_HUB_REPO}:${TIMESTAMP}
                
                # Verify deployment with timeout
                timeout 30 bash -c 'while ! curl -f http://localhost:3000/health; do sleep 2; done'
                """
            }
        }
    }

    post {
        success {
            slackSend(color: 'good', message: "✅ Pipeline SUCCESS - ${env.JOB_NAME} ${env.BUILD_NUMBER}")
            echo '🌐 Application accessible at: http://your-server-ip:3000'
        }
        failure {
            slackSend(color: 'danger', message: "❌ Pipeline FAILED - ${env.JOB_NAME} ${env.BUILD_NUMBER}")
            archiveArtifacts artifacts: '**/logs/*.log', allowEmptyArchive: true
        }
        always {
            sh """
            # Cleanup containers
            docker stop ${DOCKER_APP_NAME} ${DOCKER_TEST_NAME} || true
            docker rm ${DOCKER_APP_NAME} ${DOCKER_TEST_NAME} || true
            
            # Cleanup old images (keep last 5)
            docker image prune -f
            docker images ${DOCKER_HUB_REPO} --format "{{.ID}}" | tail -n +6 | xargs -r docker rmi -f || true
            
            # Cleanup virtualenv
            rm -rf ${VENV_NAME}
            """
        }
    }
}
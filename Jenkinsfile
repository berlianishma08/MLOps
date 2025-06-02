pipeline {
    agent any

    environment {
        TIMESTAMP = "${new Date().format('yyyyMMdd_HHmmss')}"
        DOCKER_HUB_CREDENTIALS_ID = 'jen-dockerhub'
        DOCKER_HUB_REPO = 'berlianishma08/mlops'
    }

    stages {
        stage('Checkout Repository') {
            steps {
                git credentialsId: 'jen-doc-git', url: 'https://github.com/berlianishma08/MLOps.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                python3.10 -m venv myenv && \
                . myenv/bin/activate && \
                pip install --upgrade pip setuptools wheel && \
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Data Preparation') {
            steps {
                sh '''
                . myenv/bin/activate
                python Script/data_preparation.py --data_dir Data/raw --data_new Data/clean --output_dir Model/preprocessor --target_col Survived --random_state 42 --columns_to_remove Cabin PassengerId Name --timestamp $TIMESTAMP
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                . myenv/bin/activate
                python Script/train_model.py --data_dir Data/clean --model_dir Model/model --timestamp $TIMESTAMP --model_name random_forest
                '''
            }
        }

        stage('Deploy Model') {
            steps {
                sh '''
                . myenv/bin/activate
                python Script/deploy_model.py --model_path Model/model/random_forest_$TIMESTAMP.pkl --model_dir Model/model --metadata_dir Model/metadata --timestamp $TIMESTAMP
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_HUB_REPO}:${TIMESTAMP}", ".")
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
                    // Test image dapat berjalan
                    sh '''
                    # Stop container jika sudah ada
                    docker stop mlops-test || true
                    docker rm mlops-test || true
                    
                    # Run container untuk testing
                    docker run -d --name mlops-test -p 3001:3000 mlops-local:latest
                    
                    # Wait dan test health check
                    sleep 10
                    curl -f http://localhost:3001/ || exit 1
                    
                    # Stop test container
                    docker stop mlops-test
                    docker rm mlops-test
                    '''
                }
              }
            }
        
        stage('Deploy Application') {
            steps {
                sh '''
                    # Stop aplikasi yang sedang berjalan
                    docker stop mlops-app || true
                    docker rm mlops-app || true
                    
                    # Deploy aplikasi baru
                    docker run -d --name mlops-app -p 3000:3000 --restart unless-stopped mlops-local:latest
                    
                    # Verify deployment
                    sleep 5
                    curl -f http://localhost:3000/ || exit 1
                    echo "✅ Application deployed successfully at http://localhost:3000"
                    '''
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo '🌐 Application accessible at: http://your-ec2-ip:3000'
        }
        failure {
            echo '❌ Pipeline failed. Check logs for details.'
            // Cleanup on failure
            sh '''
            docker stop mlops-app mlops-test || true
            docker rm mlops-app mlops-test || true
            '''
        }
        always {
            // Cleanup old images (keep last 3)
            sh '''
            docker image prune -f
            docker images mlops-local --format "table {{.Repository}}:{{.Tag}}" | tail -n +4 | xargs -r docker rmi || true
            '''
        }
    }
}

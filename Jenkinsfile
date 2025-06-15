pipeline {
    agent any

    environment {
        TIMESTAMP = "${new Date().format('yyyyMMdd_HHmmss')}"
        DOCKER_HUB_CREDENTIALS_ID = 'jen-dockerhub'
        DOCKER_HUB_REPO = 'berlianishma08/mlops'
        MLFLOW_TRACKING_URI = 'http://98.82.143.252:5000' 
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
                python3 -m venv myenv
                . myenv/bin/activate
                pip install --upgrade pip
                pip install setuptools wheel
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
                export MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI
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

        stage('Deploy Application') {
            steps {
                sh '''
                
                # docker run -d --name mlops -p 3000:3000 --restart unless-stopped ${DOCKER_HUB_REPO}:latest
                # sleep 5
                curl -f http://98.82.143.252:3000/ || exit 1
                echo "✅ Application deployed successfully at http://98.82.143.252:3000"
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo '🌐 Application accessible at: http://98.82.143.252:3000'
            echo "🔎 Cek hasil eksperimen di MLflow: ${MLFLOW_TRACKING_URI}"
        }
        failure {
            echo '❌ Pipeline failed. Check logs for details.'
            
        }
        always {
            sh '''
            docker image prune -f
            docker images ${DOCKER_HUB_REPO} --format "{{.Repository}}:{{.Tag}}" | tail -n +4 | xargs -r docker rmi || true
            '''
        }
    }
}

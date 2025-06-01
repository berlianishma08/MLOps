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
                python3 -m venv myenv
                . myenv/bin/activate
                pip install --upgrade pip
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
        
        stage('Deploy') {
            steps {
                sh 'docker run -d -p 5000:5000 --name mlops-app berlianishma08/mlops:latest'
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs.'
        }
    }
}

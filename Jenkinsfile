pipeline {
    agent any

    environment {
        TIMESTAMP = "${new Date().format('yyyyMMdd_HHmmss')}"
        DOCKER_HUB_CREDENTIALS_ID = 'jen-dockerhub'
        DOCKER_HUB_REPO = 'yourdockerhubusername/brawijaya-mlops'
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
                cd MLOps
                python3 -m venv myenv
                source myenv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Data Preparation') {
            steps {
                sh '''
                cd MLOps
                source myenv/bin/activate
                python Script/data_preparation.py --data_dir Data/raw --data_new Data/clean --output_dir Model/preprocessor --target_col Survived --random_state 42 --columns_to_remove Cabin PassengerId Name --timestamp $TIMESTAMP
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                cd MLOps
                source myenv/bin/activate
                python Script/train_model.py --data_dir Data/clean --model_dir Model/model --timestamp $TIMESTAMP --model_name random_forest
                '''
            }
        }

        stage('Deploy Model') {
            steps {
                sh '''
                cd MLOps
                source myenv/bin/activate
                python Script/deploy_model.py --model_path Model/model/random_forest_$TIMESTAMP.pkl --model_dir Model/model --metadata_dir Model/metadata --timestamp $TIMESTAMP
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_HUB_REPO}:${TIMESTAMP}", "MLOps/")
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

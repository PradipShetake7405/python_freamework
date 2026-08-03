
pipeline {

    agent any

    parameters {

        choice(
            name: 'ENV',
            choices: ['dev', 'qa', 'stage', 'prod'],
            description: 'Select Environment'
        )

        choice(
            name: 'BROWSER',
            choices: ['chromium', 'firefox', 'edge'],
            description: 'Select Browser'
        )

        choice(
            name: 'SUITE',
            choices: ['smoke', 'regression', 'sanity'],
            description: 'Select Test Suite'
        )

        booleanParam(
            name: 'HEADLESS',
            defaultValue: true,
            description: 'Run in Headless Mode'
        )

      }

      stage('Print Parameters') {
        steps {
            echo "Environment : ${params.ENV}"
            echo "Browser     : ${params.BROWSER}"
            echo "Suite       : ${params.SUITE}"
            echo "Headless    : ${params.HEADLESS}"
        }
    }
    stages {

        stage('Checkout') {
            steps {
                echo 'Repository checked out from GitHub'
            }
        }

        stage('Python Version') {
            steps {
                bat 'python --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Install Playwright') {
            steps {
                bat 'playwright install'
            }
        }

        stage('Run Tests') {
            steps {
                bat '  --env=${params.ENV} ^
            --browser=${params.BROWSER} ^
            --headed=${params.HEADLESS} ^
            -m ${params.SUITE}'
            }
        }

    }

    post {

        success {
            echo 'Build Successful'
        }

        failure {
            echo 'Build Failed'
        }

        always {
            echo 'Pipeline Completed'
        }

    }

}
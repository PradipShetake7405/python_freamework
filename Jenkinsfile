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
            description: 'Run browser in Headless Mode'
        )

    }

    stages {

        stage('Print Parameters') {
            steps {
                echo "===================================="
                echo "Build Parameters"
                echo "===================================="
                echo "Environment : ${params.ENV}"
                echo "Browser     : ${params.BROWSER}"
                echo "Suite       : ${params.SUITE}"
                echo "Headless    : ${params.HEADLESS}"
                echo "===================================="
            }
        }

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

        stage('Install Playwright Browsers') {
            steps {
                bat 'playwright install'
            }
        }

        stage('Run Tests') {
            steps {
                bat """
                pytest ^
                --env=${params.ENV} ^
                --browser=${params.BROWSER} ^
                -m ${params.SUITE}
                """
            }
        }

    }

    post {

        success {
            echo '✅ Build Successful'
        }

        failure {
            echo '❌ Build Failed'
        }

        always {
            echo '===================================='
            echo 'Pipeline Completed'
            echo '===================================='
        }

    }

}
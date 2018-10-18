pipeline {
    agent none
    stages {
        stage('Build') {
            agent {
                docker {
                    image 'python:2-alpine'
                }
            }
            steps {
                sh 'python -m py_compile oef_python/*.py
            }
        }
        stage('Test') {
            agent {
                docker {
                    image 'qnib/pytest'
                }
            }
            steps {
                sh 'PYTHONPATH=$PYTHONPATH:./oef_python py.test --verbose --cov=test_oef_python'
            }
            post {
                always {
                    codecov
                }
            }
        }
    }
}

pipeline {

    agent {
        docker {
            image 'gcr.io/organic-storm-201412/python-ci'
            }
         }

    stages {
        stage('Build') {

            steps {
                sh 'pip install -r requirements.txt'
                sh 'python3 -m py_compile oef_python/*.py'
            }
        }
        stage('Test') {
            steps {
                sh 'PYTHONPATH=$PYTHONPATH:./oef_python pytest --verbose --cov=oef_python ./test_oef_python'
            }

        }
    }
}

pipeline {

    agent {
        docker {
            image 'gcr.io/organic-storm-201412/python-ci'
            }
         }

    stages {
        stage('Build') {

            steps {
                sh 'apt-get install -y protobuf-compiler'
                sh 'pip install -r requirements.txt'
                sh 'python setup.py install'
                sh 'python3 -m py_compile oef_python/*.py'
            }
        }
        stage('Test') {
            steps {
                sh 'PYTHONPATH=$PYTHONPATH:./oef_python pytest --verbose --cov=oef_python ./test'
            }

        }
    }
}

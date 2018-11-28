pipeline {

    agent {
        docker {
            image 'gcr.io/organic-storm-201412/python-ci'
            }
        }

    stages {


        stage('Pre-build'){

            steps {
                sh 'apt-get install -y protobuf-compiler'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Builds & Tests'){

            parallel{

                stage('Build') {
                    steps {
                        sh 'python setup.py install'
                        sh 'python3 -m py_compile oef/*.py'
                    }
                }

                stage('Test') {
                    steps {
                        sh 'PYTHONPATH=$PYTHONPATH:./oef pytest --verbose --cov=oef ./test'
                    }
                }
                stage('Lint'){
                    steps{
                        sh 'flake8 oef_python'
                        // TODO remove the --disable-all flag
                        sh 'pylint -d all oef/api.py'
                    }
                }

                stage('Build docs'){
                    steps{
                        sh 'cd docs && make html'
                    }
                }
            }

        }

    }
}

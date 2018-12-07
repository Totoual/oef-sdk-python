pipeline {

    agent {
        docker {
                image "gcr.io/organic-storm-201412/oef-python-ci-build:latest"
            }
        }

    stages {


        stage('Pre-build'){

            steps {
                sh 'apt-get install -y protobuf-compiler'
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('Builds & Tests'){

            parallel{

                stage('Build & Test'){
                    stages{
                        stage('Build') {
                            steps {
                                sh 'python3 setup.py install'
                                sh 'python3 -m py_compile oef/*.py'
                            }
                        }
                        stage('Test') {
                            steps {
                                dir ("OEFCore"){
                                    git url: 'https://github.com/uvue-git/OEFCore.git'
                                }
                                sh 'cd OEFCore && mkdir build && cd build && cmake .. && make -j4'
                                sh 'pytest --verbose --cov=oef ./test'
                            }
                        }
                    }
                }

                stage('Lint'){
                    steps{
                        // TODO remove the "disable all" flags.
                        sh 'flake8 --exclude=.*'
                        sh 'pylint -d all oef'
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

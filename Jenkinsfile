pipeline {

    agent {
        docker {
            image "gcr.io/organic-storm-201412/oef-sdk-python-image:latest"
            }
        }

    stages {

        stage('Pre-build'){

            steps {
                sh 'pipenv run pipenv install --dev'
                sh 'pipenv run python3 scripts/setup_test.py'
            }
        }

        stage('Builds & Tests'){

            parallel{

                stage('Test') {
                    steps {
                        sh 'pipenv run tox -e py36'
                    }
                }

                stage('Lint'){
                    steps{
                        sh 'pipenv run flake8 oef --exclude=oef/*_pb2.py'
                        sh 'pipenv run pylint -d all oef'
                    }
                }

                stage('Docs'){
                    steps{
                        sh 'cd docs && pipenv run make html'
                    }
                }

            }

        }

    }
}

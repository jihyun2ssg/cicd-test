pipeline {
  agent any

  // 🕒 테스트용: 10분마다 자동 실행 (한국시간)
  triggers {
    cron('''TZ=Asia/Seoul
H/10 * * * *''')
  }

  options {
    // 최근 20개 빌드 로그만 보관
    buildDiscarder(logRotator(numToKeepStr: '20'))
    timestamps()
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Setup venv & deps (Windows)') {
      when { expression { !isUnix() } }
      steps {
        bat '''
        echo ===== [Setup venv & install deps] =====
        if not exist .venv (
          py -3 -m venv .venv
        )

        .venv\\Scripts\\python -m pip install --upgrade pip

        if exist requirements.txt (
          .venv\\Scripts\\pip install -r requirements.txt
        )

        REM ✅ Playwright 브라우저 자동 설치
        .venv\\Scripts\\python -m playwright install chromium
        '''
      }
    }

    stage('Run script (Windows)') {
      when { expression { !isUnix() } }
      steps {
        bat '''
        echo ===== [Run capture script] =====
        if not exist screenshots mkdir screenshots
        .venv\\Scripts\\python main.py
        '''
      }
    }
  }

  post {
    always {
      // ✅ Jenkins Build Artifacts에 모든 스크린샷 저장
      archiveArtifacts artifacts: 'screenshots/**/*.png', allowEmptyArchive: true
    }
    success {
      echo '🎉 Build success - screenshots archived.'
    }
    failure {
      echo '❌ Build failed.'
    }
  }
}
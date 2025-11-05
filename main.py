import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
import sys

# Jenkins 콘솔 인코딩 깨짐 방지
sys.stdout.reconfigure(encoding='utf-8')


def upload_to_drive(file_path):
    gauth = GoogleAuth()

    # ✅ Jenkins용: 기존 토큰 재사용 / 무인 인증
    # credentials.json + token.json이 같은 경로에 있어야 함
    gauth.LoadCredentialsFile("token.json")
    if gauth.credentials is None:
        # 처음 로컬에서 token.json 생성 후 Jenkins로 복사 필요
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile("token.json")
    elif gauth.access_token_expired:
        gauth.Refresh()
        gauth.SaveCredentialsFile("token.json")
    else:
        gauth.Authorize()

    drive = GoogleDrive(gauth)

    folder_id = "1TxwpqSB0Xuhvdc1nDmmLZkpVWrjO1Pqs"  # ✅ 업로드할 Google Drive 폴더 ID
    file_name = os.path.basename(file_path)

    gfile = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})
    gfile.SetContentFile(file_path)
    gfile.Upload()
    print(f"[OK] Google Drive 업로드 완료: {file_name}")


async def capture_full_page():
    os.makedirs("screenshots", exist_ok=True)

    async with async_playwright() as p:
        # ✅ Jenkins는 반드시 headless=True 이어야 함
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto("https://www.naver.com", wait_until="load", timeout=60000)

            # ✅ networkidle은 상용 사이트에선 너무 오래 걸리므로 load로 충분
            await page.wait_for_load_state("load")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/ssg_{timestamp}.png"
            await page.screenshot(path=filename, full_page=True)
            print(f"[OK] 스크린샷 저장됨: {filename}")

            upload_to_drive(filename)

        except Exception as e:
            print(f"[ERROR] 캡처 중 오류 발생: {str(e)}")

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(capture_full_page())

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

def upload_to_drive(file_path):
    gauth = GoogleAuth()
    # 최초 1회 실행 시 브라우저 열림 → 로그인 후 token.json 생성됨
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    folder_id = "1TxwpqSB0Xuhvdc1nDmmLZkpVWrjO1Pqs"  # ✅ 업로드할 폴더 ID 입력
    file_name = os.path.basename(file_path)

    gfile = drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})
    gfile.SetContentFile(file_path)
    gfile.Upload()
    print(f"✅ Uploaded to Google Drive: {file_name}")

async def capture_full_page():
    os.makedirs("screenshots", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 타임아웃 시간을 100초로 늘리고, load 이벤트로 변경
            await page.goto(
                "https://www.naver.com", 
                wait_until="load",
                timeout=100000
            )
            
            # 페이지 로딩 후 추가 대기
            await page.wait_for_load_state("networkidle", timeout=100000)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/ssg_{timestamp}.png"
            await page.screenshot(path=filename, full_page=True)
            print(f"✅ 스크린샷 저장됨: {filename}")
            
            upload_to_drive(filename)
            
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_full_page())
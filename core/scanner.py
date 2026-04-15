import sys, time, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def auto_learn(niche_url):
    print(f"[LEARNING] Memasuki Niche: {niche_url}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(niche_url)
        time.sleep(5)
        
        # Ambil Judul dan Seluruh Teks untuk Database AI
        page_title = driver.title
        data = driver.find_element(By.TAG_NAME, "body").text
        
        # Simpan secara Terstruktur
        folder = "knowledge_base"
        if not os.path.exists(folder): os.makedirs(folder)
        
        filename = f"{folder}/study_{int(time.time())}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# DATA RESEARCH: {page_title}\n")
            f.write(f"SOURCE: {niche_url}\n\n")
            f.write(data)
            
        print(f"[SUCCESS] Ilmu baru disimpan di {filename}")
        
        # OTOMATIS PUSH KE GITHUB Kingkana22
        os.system("git add .")
        os.system(f'git commit -m "Bot Learned from {page_title}"')
        os.system("git push origin master")
        
    except Exception as e:
        print(f"[FAILED] Gagal menyerap ilmu: {e}")
    finally:
        driver.quit()
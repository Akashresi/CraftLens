import os
import subprocess

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Figure 4.4: Mobile Voice Catalog Screen</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background-color: #F8F6F0;
    color: #242B27;
    padding: 30px;
    width: 1200px;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 1050px;
  }
  .wrapper {
    display: flex;
    gap: 40px;
    align-items: center;
    max-width: 1140px;
  }

  /* Phone Mockup */
  .phone-frame {
    width: 440px;
    height: 940px;
    background: #FFFFFF;
    border-radius: 48px;
    box-shadow: 0 25px 60px -15px rgba(36, 43, 39, 0.2), 0 0 0 10px #242B27, 0 0 0 12px #D9D4C7;
    overflow: hidden;
    position: relative;
    display: flex;
    flex-direction: column;
    border: 3px solid #242B27;
  }

  /* Phone Notch & Status Bar */
  .phone-header {
    background: #FFFFFF;
    padding: 12px 24px 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
    font-weight: 700;
    color: #242B27;
    border-bottom: 1px solid #F0ECE1;
  }
  .dynamic-island {
    position: absolute;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    width: 110px;
    height: 26px;
    background: #242B27;
    border-radius: 20px;
    z-index: 50;
  }

  /* App Navigation */
  .app-nav {
    background: #FFFFFF;
    padding: 10px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #E8E5DC;
  }
  .nav-title {
    font-size: 17px;
    font-weight: 800;
    color: #285C45;
  }
  .nav-sub {
    font-size: 11px;
    color: #858B83;
  }

  /* Language Selector Bar */
  .lang-bar {
    display: flex;
    gap: 6px;
    padding: 10px 16px;
    background: #FAF8F5;
    border-bottom: 1px solid #E8E5DC;
    overflow-x: hidden;
  }
  .lang-chip {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    border: 1px solid #E8E5DC;
    background: #FFFFFF;
    color: #242B27;
  }
  .lang-active {
    background: #285C45;
    color: #FFFFFF;
    border-color: #285C45;
  }

  /* Screen Scrollable Body */
  .screen-body {
    flex: 1;
    overflow-y: hidden;
    padding: 14px 16px;
    background: #F8F6F0;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  /* Voice Recording Card */
  .voice-card {
    background: #FFFFFF;
    border: 1px solid #E8E5DC;
    border-radius: 16px;
    padding: 14px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 2px 8px rgba(36,43,39,0.04);
  }
  .mic-button {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: #285C45;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    box-shadow: 0 0 0 6px #EAF2ED;
    flex-shrink: 0;
  }
  .wave-bars {
    display: flex;
    align-items: center;
    gap: 3px;
    height: 24px;
    flex: 1;
  }
  .bar {
    width: 4px;
    background: #C47B52;
    border-radius: 2px;
  }

  /* Spoken Transcript Card */
  .transcript-card {
    background: #FAF6EF;
    border: 1px solid #E4DAC9;
    border-left: 4px solid #C47B52;
    border-radius: 10px;
    padding: 10px 12px;
  }
  .transcript-label {
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    color: #C47B52;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .transcript-text {
    font-size: 12px;
    font-weight: 600;
    line-height: 1.5;
    color: #242B27;
  }

  /* AI Catalog Result Card */
  .catalog-card {
    background: #FFFFFF;
    border: 1px solid #E8E5DC;
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0 2px 8px rgba(36,43,39,0.04);
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .catalog-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #F0ECE1;
    padding-bottom: 8px;
  }
  .catalog-title-badge {
    font-size: 11px;
    font-weight: 800;
    color: #285C45;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .field-box {
    background: #FAF8F5;
    border: 1px solid #E8E5DC;
    border-radius: 8px;
    padding: 8px 10px;
  }
  .field-name {
    font-size: 9px;
    font-weight: 800;
    text-transform: uppercase;
    color: #858B83;
    margin-bottom: 2px;
  }
  .field-val-en {
    font-size: 12px;
    font-weight: 700;
    color: #242B27;
    line-height: 1.35;
  }
  .field-val-hi {
    font-size: 11px;
    font-weight: 600;
    color: #5A4E3E;
    margin-top: 2px;
  }

  .spec-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .keywords-tag {
    font-size: 10px;
    font-family: monospace;
    color: #285C45;
    font-weight: 700;
    line-height: 1.4;
  }

  /* Mobile Footer Buttons */
  .app-footer {
    background: #FFFFFF;
    border-top: 1px solid #E8E5DC;
    padding: 12px 16px 20px;
    display: flex;
    gap: 10px;
  }
  .btn-draft {
    flex: 1;
    padding: 11px;
    border-radius: 10px;
    background: #FFFFFF;
    border: 1px solid #E8E5DC;
    font-size: 12px;
    font-weight: 700;
    color: #242B27;
    text-align: center;
  }
  .btn-price {
    flex: 1.4;
    padding: 11px;
    border-radius: 10px;
    background: #285C45;
    font-size: 12px;
    font-weight: 700;
    color: #FFFFFF;
    text-align: center;
    box-shadow: 0 2px 6px rgba(40,92,69,0.3);
  }

  /* Side Annotation Card */
  .annotation-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  .info-card {
    background: #FFFFFF;
    border: 1px solid #E8E5DC;
    border-radius: 14px;
    padding: 24px;
    box-shadow: 0 4px 12px rgba(36,43,39,0.05);
  }
  .info-title {
    font-size: 18px;
    font-weight: 800;
    color: #285C45;
    margin-bottom: 8px;
  }
  .info-desc {
    font-size: 13px;
    color: #636A64;
    line-height: 1.6;
    margin-bottom: 16px;
  }
  .bullet-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .bullet-item {
    font-size: 13px;
    color: #242B27;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    line-height: 1.4;
  }
  .bullet-icon {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #EAF2ED;
    color: #285C45;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 11px;
    flex-shrink: 0;
    margin-top: 1px;
  }
  .api-swagger-badge {
    background: #FAF6EF;
    border: 1px solid #E4DAC9;
    border-radius: 8px;
    padding: 10px 14px;
    font-family: monospace;
    font-size: 12px;
    color: #285C45;
    font-weight: 700;
  }
</style>
</head>
<body>

<div class="wrapper">
  <!-- Mobile Device Frame -->
  <div class="phone-frame">
    <div class="dynamic-island"></div>
    <div class="phone-header">
      <span>9:41</span>
      <span style="letter-spacing: 1px;">5G 100%</span>
    </div>

    <div class="app-nav">
      <div>
        <div class="nav-title">Voice AI Cataloger</div>
        <div class="nav-sub">Speak naturally in mother tongue</div>
      </div>
      <span style="font-size: 18px;">✨</span>
    </div>

    <div class="lang-bar">
      <div class="lang-chip lang-active">தமிழ் (Tamil)</div>
      <div class="lang-chip">हिंदी (Hindi)</div>
      <div class="lang-chip">English</div>
      <div class="lang-chip">తెలుగు</div>
      <div class="lang-chip">ಕನ್ನಡ</div>
      <div class="lang-chip">മലയാളം</div>
    </div>

    <div class="screen-body">
      <!-- Voice Recording Card -->
      <div class="voice-card">
        <div class="mic-button">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
            <line x1="8" y1="23" x2="16" y2="23"/>
          </svg>
        </div>
        <div style="flex: 1;">
          <div style="font-size: 12px; font-weight: 700; color: #285C45;">Voice Capture Active</div>
          <div class="wave-bars">
            <div class="bar" style="height: 10px;"></div>
            <div class="bar" style="height: 18px;"></div>
            <div class="bar" style="height: 24px;"></div>
            <div class="bar" style="height: 14px;"></div>
            <div class="bar" style="height: 20px;"></div>
            <div class="bar" style="height: 16px;"></div>
            <div class="bar" style="height: 22px;"></div>
            <div class="bar" style="height: 12px;"></div>
            <div class="bar" style="height: 19px;"></div>
            <div class="bar" style="height: 11px;"></div>
            <div class="bar" style="height: 16px;"></div>
          </div>
          <div style="font-size: 10px; color: #858B83; margin-top: 2px;">0:06 / 0:15 sec • Tamil ASR</div>
        </div>
      </div>

      <!-- Spoken Transcript -->
      <div class="transcript-card">
        <div class="transcript-label">
          <span>🎙️ Spoken Tamil Audio Transcript (Bhashini ASR)</span>
        </div>
        <div class="transcript-text">
          "இது விளாச்சேரி வண்டல் மண்ணில் செய்யப்பட்ட பாரம்பரிய ஐயனார் குதிரை சிலை. இயற்கை வர்ணங்கள் கொண்டு 6 மணி நேரம் கைகளால் செதுக்கப்பட்டது."
        </div>
      </div>

      <!-- AI Extracted Catalog -->
      <div class="catalog-card">
        <div class="catalog-header">
          <span class="catalog-title-badge">
            <span>✨ AI Truthful Catalog Generation</span>
          </span>
          <span style="font-size: 10px; font-weight: 700; color: #32815A; background: #EAF2ED; padding: 2px 8px; border-radius: 4px;">
            Verified Truthful
          </span>
        </div>

        <div class="field-box">
          <div class="field-name">Product Titles (EN / HI)</div>
          <div class="field-val-en">Handcrafted Vilachery Terracotta Ayyanar Figurine</div>
          <div class="field-val-hi">हस्तनिर्मित विलाचेरी टेराकोटा अय्यनार मिट्टी की मूर्ति</div>
        </div>

        <div class="field-box">
          <div class="field-name">Craft Description</div>
          <div class="field-val-en" style="font-size: 11px; font-weight: 500;">
            Authentic wheel-thrown and hand-sculpted terracotta Ayyanar clay sculpture created from natural Vaigai river alluvial silt. Kiln-fired using traditional rice husk combustion with organic mineral slip glazes.
          </div>
        </div>

        <div class="spec-grid">
          <div class="field-box">
            <div class="field-name">Extracted Materials</div>
            <div class="field-val-en" style="font-size: 11px;">River Silt Clay, Husk, Natural Pigments</div>
          </div>
          <div class="field-box">
            <div class="field-name">Technique & Labor</div>
            <div class="field-val-en" style="font-size: 11px;">Wheel & Hand Craft (6.5 Hrs)</div>
          </div>
        </div>

        <div class="field-box">
          <div class="field-name">SEO & Marketplace Keywords</div>
          <div class="keywords-tag">#VilacheryPottery #Terracotta #Ayyanar #GI412 #Handmade #DirectArtisan</div>
        </div>
      </div>
    </div>

    <!-- App Action Buttons -->
    <div class="app-footer">
      <div class="btn-draft">Save Offline Draft</div>
      <div class="btn-price">Calculate Fair Price →</div>
    </div>
  </div>

  <!-- Side Annotation & System Architecture Context -->
  <div class="annotation-box">
    <div class="info-card">
      <div style="font-size: 12px; font-weight: 800; color: #C47B52; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">
        Figure 4.4 Documentation
      </div>
      <div class="info-title">Multilingual Voice-First Cataloging Interface</div>
      <div class="info-desc">
        CraftLens 2.0 provides an accessible, voice-first mobile interface designed for artisans with low digital literacy. Master craftspeople simply speak about their handmade product in their regional mother tongue.
      </div>

      <ul class="bullet-list">
        <li class="bullet-item">
          <div class="bullet-icon">1</div>
          <div>
            <strong>Regional Speech Recognition (ASR):</strong> Accurately transcribes regional dialects across Tamil, Hindi, Telugu, Kannada, Malayalam, and English.
          </div>
        </li>
        <li class="bullet-item">
          <div class="bullet-icon">2</div>
          <div>
            <strong>Strict Anti-Hallucination Pipeline:</strong> The LLM prompt explicitly forbids inventing synthetic certifications, fake materials, or unauthorized GI claims.
          </div>
        </li>
        <li class="bullet-item">
          <div class="bullet-icon">3</div>
          <div>
            <strong>Bi-Directional Translation:</strong> Generates polished, SEO-optimized English titles and descriptions for global export, as well as Hindi for domestic retail.
          </div>
        </li>
        <li class="bullet-item">
          <div class="bullet-icon">4</div>
          <div>
            <strong>Offline SQLite Draft Persistence:</strong> Works in rural workshops without continuous cellular internet; drafts sync automatically upon network reconnection.
          </div>
        </li>
      </ul>

      <div style="margin-top: 20px;">
        <div class="api-swagger-badge">
          POST /api/v1/voice/generate-catalog &rarr; 200 OK (840ms)
        </div>
      </div>
    </div>
  </div>
</div>

</body>
</html>
"""

with open("photos/fig_4_4.html", "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_img = r"D:\projects\KD\SIH26090\photos\Figure_4.4_Mobile_Voice_Catalog.png"

args = [
    chrome_path,
    "--headless=new",
    "--no-sandbox",
    "--disable-gpu",
    "--window-size=1200,1050",
    f"--screenshot={out_img}",
    "file:///D:/projects/KD/SIH26090/photos/fig_4_4.html",
]

res = subprocess.run(args, capture_output=True, text=True)
print("Return code:", res.returncode)
print("File exists:", os.path.exists(out_img))
if os.path.exists(out_img):
    print("File size:", os.path.getsize(out_img), "bytes")

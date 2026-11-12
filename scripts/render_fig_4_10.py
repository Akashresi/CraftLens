import os
import subprocess

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Figure 4.10: Artisan Dashboard</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background-color: #EFECE6;
    color: #242B27;
    padding: 30px;
    width: 1440px;
    min-height: 1020px;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  /* Browser Window Mockup */
  .browser-window {
    width: 1380px;
    background: #F8F6F0;
    border-radius: 16px;
    box-shadow: 0 25px 60px -15px rgba(36, 43, 39, 0.25), 0 0 0 1px #D9D4C7;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  /* Browser Chrome Bar */
  .browser-top {
    background: #E8E4DA;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 16px;
    border-bottom: 1px solid #D5CFC3;
  }
  .window-dots {
    display: flex;
    gap: 7px;
  }
  .dot {
    width: 11px;
    height: 11px;
    border-radius: 50%;
  }
  .dot-red { background: #FF5F56; }
  .dot-yellow { background: #FFBD2E; }
  .dot-green { background: #27C93F; }

  .url-bar {
    flex: 1;
    background: #FFFFFF;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    color: #555E57;
    display: flex;
    align-items: center;
    gap: 8px;
    border: 1px solid #D5CFC3;
    max-width: 650px;
  }
  .url-lock {
    color: #285C45;
    font-weight: 800;
  }

  /* In-App Navbar */
  .app-nav {
    background: #FFFFFF;
    border-bottom: 1px solid #E8E5DC;
    padding: 12px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .brand-logo {
    width: 34px;
    height: 34px;
    background: #285C45;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    font-weight: 800;
    font-size: 16px;
  }
  .brand-text {
    font-size: 18px;
    font-weight: 800;
    color: #285C45;
  }
  .brand-tag {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    color: #858B83;
    display: block;
    margin-top: -2px;
  }

  .nav-links {
    display: flex;
    gap: 22px;
    font-size: 13px;
    font-weight: 600;
    color: #555E57;
  }
  .nav-link-active {
    color: #285C45;
    font-weight: 800;
    border-bottom: 2px solid #285C45;
    padding-bottom: 2px;
  }

  .user-badge {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #FAF8F5;
    border: 1px solid #E8E5DC;
    padding: 6px 12px;
    border-radius: 8px;
  }
  .user-avatar {
    width: 28px;
    height: 28px;
    background: #C47B52;
    border-radius: 50%;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .user-name {
    font-size: 12px;
    font-weight: 700;
    color: #242B27;
  }
  .user-cluster {
    font-size: 10px;
    color: #32815A;
    font-weight: 600;
  }

  /* Dashboard Content */
  .dash-body {
    padding: 24px 28px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  /* Metric Cards Grid */
  .metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
  }
  .metric-card {
    background: #FFFFFF;
    border: 1px solid #E8E5DC;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 2px 6px rgba(36,43,39,0.03);
  }
  .metric-label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    color: #858B83;
    margin-bottom: 6px;
  }
  .metric-val {
    font-size: 26px;
    font-weight: 800;
    color: #242B27;
  }
  .metric-sub {
    font-size: 11px;
    font-weight: 700;
    margin-top: 4px;
  }
  .sub-green { color: #32815A; }
  .sub-orange { color: #C47B52; }
  .sub-warn { color: #D69B43; }

  /* Two Column Main Section */
  .main-split {
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 20px;
  }

  /* AI Assistant Chat Card */
  .chat-card {
    background: #FFFFFF;
    border: 1px solid #E8E5DC;
    border-radius: 14px;
    padding: 18px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 8px rgba(36,43,39,0.04);
  }
  .card-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #F0ECE1;
    padding-bottom: 12px;
    margin-bottom: 14px;
  }
  .card-title {
    font-size: 14px;
    font-weight: 800;
    color: #285C45;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .chat-stream {
    display: flex;
    flex-direction: column;
    gap: 14px;
    height: 380px;
    overflow-y: hidden;
  }

  .chat-bubble-user {
    align-self: flex-end;
    background: #285C45;
    color: #FFFFFF;
    border-radius: 14px 14px 2px 14px;
    padding: 12px 16px;
    max-width: 80%;
    font-size: 13px;
    font-weight: 600;
    line-height: 1.4;
    box-shadow: 0 2px 6px rgba(40,92,69,0.2);
  }
  .chat-bubble-ai {
    align-self: flex-start;
    background: #FAF8F5;
    border: 1px solid #E8E5DC;
    color: #242B27;
    border-radius: 14px 14px 14px 2px;
    padding: 14px 18px;
    max-width: 88%;
    font-size: 13px;
    line-height: 1.5;
  }
  .ai-source-pill {
    display: inline-block;
    background: #EAF2ED;
    color: #285C45;
    font-size: 10px;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 6px;
  }

  .chat-input-bar {
    margin-top: 14px;
    border-top: 1px solid #F0ECE1;
    padding-top: 12px;
    display: flex;
    gap: 10px;
  }
  .chat-input {
    flex: 1;
    background: #FAF8F5;
    border: 1px solid #E8E5DC;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 12px;
    color: #242B27;
  }
  .chat-send-btn {
    background: #285C45;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 10px 18px;
    font-size: 12px;
    font-weight: 700;
  }

  /* Right Side: Orders Table + Marketing */
  .right-column {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .orders-card {
    background: #FFFFFF;
    border: 1px solid #E8E5DC;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 2px 8px rgba(36,43,39,0.04);
  }
  .orders-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }
  .orders-table th {
    text-align: left;
    padding: 8px 10px;
    font-size: 10px;
    font-weight: 800;
    color: #858B83;
    text-transform: uppercase;
    border-bottom: 1px solid #E8E5DC;
  }
  .orders-table td {
    padding: 10px 10px;
    border-bottom: 1px solid #F0ECE1;
    color: #242B27;
  }
  .status-pill {
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
  }
  .status-ready { background: #FFF4E5; color: #B76E00; }
  .status-shipped { background: #EAF2ED; color: #285C45; }
  .status-escrow { background: #FBF0EB; color: #C47B52; }

  /* Marketing Card */
  .marketing-card {
    background: #FFFFFF;
    border: 1px solid #E8E5DC;
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(36,43,39,0.04);
  }
  .social-preview {
    background: #FAF8F5;
    border: 1px solid #E8E5DC;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 11px;
    line-height: 1.45;
    color: #333C37;
    margin-top: 8px;
  }
</style>
</head>
<body>

<div class="browser-window">
  <!-- Chrome Top Navigation -->
  <div class="browser-top">
    <div class="window-dots">
      <div class="dot dot-red"></div>
      <div class="dot dot-yellow"></div>
      <div class="dot dot-green"></div>
    </div>
    <div class="url-bar">
      <span class="url-lock">🔒</span>
      <span>https://craftlens.in/artisan/dashboard</span>
    </div>
    <span style="font-size: 11px; color: #858B83; font-weight: 600;">Production Environment • MoSJE SIH26090</span>
  </div>

  <!-- In-App Header -->
  <div class="app-nav">
    <div class="brand">
      <div class="brand-logo">CL</div>
      <div>
        <div class="brand-text">CraftLens</div>
        <span class="brand-tag">Artisan Business Hub</span>
      </div>
    </div>

    <div class="nav-links">
      <span>Marketplace Catalog</span>
      <span>GI Heritage Origins</span>
      <span>B2B Wholesale</span>
      <span class="nav-link-active">Artisan Hub</span>
    </div>

    <div class="user-badge">
      <div class="user-avatar">MS</div>
      <div>
        <div class="user-name">Meenakshi Sundaram</div>
        <div class="user-cluster">Vilachery Pottery • GI-TN-412</div>
      </div>
    </div>
  </div>

  <!-- Dashboard Body -->
  <div class="dash-body">
    <!-- Top Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-label-row">
          <span>Monthly Revenue</span>
          <span>📈</span>
        </div>
        <div class="metric-val">₹48,600</div>
        <div class="metric-sub sub-green">+18% vs. prior month</div>
      </div>

      <div class="metric-card">
        <div class="metric-label-row">
          <span>Direct Fair Wages</span>
          <span>✨</span>
        </div>
        <div class="metric-val" style="color: #C47B52;">₹32,400</div>
        <div class="metric-sub sub-orange">100% direct bank payout</div>
      </div>

      <div class="metric-card">
        <div class="metric-label-row">
          <span>Completed Orders</span>
          <span>📦</span>
        </div>
        <div class="metric-val">28 Orders</div>
        <div class="metric-sub sub-green">Retail & B2B combined</div>
      </div>

      <div class="metric-card">
        <div class="metric-label-row">
          <span>Low Inventory Alert</span>
          <span>⚠️</span>
        </div>
        <div class="metric-val" style="color: #D69B43;">1 Item</div>
        <div class="metric-sub sub-warn">Terracotta Diya Set (2 left)</div>
      </div>
    </div>

    <!-- Main Content Split -->
    <div class="main-split">
      <!-- Left: AI Assistant Chat -->
      <div class="chat-card">
        <div class="card-header-bar">
          <div class="card-title">
            <span>✨ AI Business Assistant (வணக்கம்! / Hello!)</span>
          </div>
          <span style="font-size: 11px; font-weight: 700; color: #285C45; background: #EAF2ED; padding: 3px 8px; border-radius: 6px;">
            Connected to Production DB
          </span>
        </div>

        <div class="chat-stream">
          <!-- Artisan Message -->
          <div class="chat-bubble-user">
            "இந்த வாரம் எந்த பொருள் அதிகம் விற்றது? மற்றும் இருப்பு விவரம் என்ன?"
            <div style="font-size: 10px; color: #D5E5DC; margin-top: 4px; font-weight: 500;">
              (Translation: Which product sold most this week and what is the current stock status?)
            </div>
          </div>

          <!-- AI Response -->
          <div class="chat-bubble-ai">
            <div class="ai-source-pill">⚡ Real-Time Sales & Inventory Query Result</div>
            <p style="font-weight: 600; color: #285C45; margin-bottom: 6px;">
              வணக்கம் மீனாட்சி சுந்தரம் அவர்களே!
            </p>
            <p style="margin-bottom: 8px;">
              1. <strong>அதிகம் விற்ற பொருள்:</strong> உங்கள் <em>'விளாச்சேரி பாரம்பரிய ஐயனார் குதிரை சிலை'</em> தயாரிப்புக்கு இந்த வாரம் <strong>14 புதிய ஆர்டர்கள்</strong> வந்துள்ளன (மொத்த வருமானம் ₹25,900; உங்கள் நேரடி நியாயமான ஊதியம் ₹13,300).
            </p>
            <p style="margin-bottom: 8px;">
              2. <strong>இருப்பு எச்சரிக்கை:</strong> வரவிருக்கும் திருவிழா தேவை காரணமாக <em>'பாரம்பரிய அகல் விளக்குகள்'</em> இருப்பு <strong>2 அலகுகளாகக் குறைந்துள்ளது</strong>.
            </p>
            <p style="color: #C47B52; font-weight: 600;">
              💡 பரிந்துரை: அடுத்த 3 நாட்களில் குறைந்தபட்சம் 20 அகல் விளக்கு அலகுகளைத் தயாரித்து உலை சுட வைக்க பரிந்துரைக்கிறேன்.
            </p>
          </div>
        </div>

        <div class="chat-input-bar">
          <input type="text" class="chat-input" value="Ask about sales, pricing, or orders in Tamil, Hindi or English..." readonly>
          <button class="chat-send-btn">Send Voice/Text</button>
        </div>
      </div>

      <!-- Right: Orders Table + Marketing -->
      <div class="right-column">
        <div class="orders-card">
          <div class="card-header-bar">
            <div class="card-title">
              <span>📋 Recent Orders & Shipments</span>
            </div>
            <span style="font-size: 11px; font-weight: 700; color: #285C45;">View Full Log</span>
          </div>

          <table class="orders-table">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Craft Item</th>
                <th>Payout</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>#ORD-94812</strong></td>
                <td>Vilachery Ayyanar Figurine</td>
                <td><strong>₹950</strong> (Wage)</td>
                <td><span class="status-pill status-ready">Ready to Pack</span></td>
              </tr>
              <tr>
                <td><strong>#ORD-94751</strong></td>
                <td>Terracotta Diya Set (x6)</td>
                <td><strong>₹420</strong> (Wage)</td>
                <td><span class="status-pill status-shipped">Dispatched</span></td>
              </tr>
              <tr>
                <td><strong>#B2B-2041</strong></td>
                <td>100x Bulk Clay Sculptures</td>
                <td><strong>₹42,000</strong> (Adv)</td>
                <td><span class="status-pill status-escrow">Escrow Active</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="marketing-card">
          <div class="card-header-bar">
            <div class="card-title">
              <span>📢 1-Click AI Marketing Assistant</span>
            </div>
            <span style="font-size: 10px; font-weight: 700; background: #FAF6EF; color: #C47B52; padding: 2px 6px; border-radius: 4px;">
              Social Ready
            </span>
          </div>

          <div style="font-size: 11px; font-weight: 700; color: #242B27;">Generated WhatsApp & Instagram Post:</div>
          <div class="social-preview">
            ✨ <em>"விளாச்சேரி பாரம்பரிய கைவினை மண்பாண்ட சிலைகள் மற்றும் அகல் விளக்குகள் இப்போது நேரடியாக எங்களிடமிருந்து கிடைக்கும்! 🏺🌿 100% இயற்கை வைகை ஆற்று வண்டல் மண். நேரடி ஆர்டருக்கு CraftLens இணைப்பை கிளிக் செய்யவும். #VocalForLocal"</em>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

</body>
</html>
"""

with open("photos/fig_4_10.html", "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_img = r"D:\projects\KD\SIH26090\photos\Figure_4.10_Artisan_Dashboard.png"

args = [
    chrome_path,
    "--headless=new",
    "--no-sandbox",
    "--disable-gpu",
    "--window-size=1440,1020",
    f"--screenshot={out_img}",
    "file:///D:/projects/KD/SIH26090/photos/fig_4_10.html",
]

res = subprocess.run(args, capture_output=True, text=True)
print("Return code:", res.returncode)
print("File exists:", os.path.exists(out_img))
if os.path.exists(out_img):
    print("File size:", os.path.getsize(out_img), "bytes")

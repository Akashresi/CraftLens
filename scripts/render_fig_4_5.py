import os
import subprocess

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Figure 4.5: Pricing Calculator Result</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background-color: #F8F6F0;
    color: #242B27;
    padding: 32px;
    width: 1400px;
    min-height: 920px;
  }

  .header {
    border-bottom: 2px solid #E8E5DC;
    padding-bottom: 16px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }
  .fig-tag {
    font-size: 13px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #C47B52;
    margin-bottom: 4px;
  }
  .title {
    font-size: 26px;
    font-weight: 800;
    color: #285C45;
    letter-spacing: -0.5px;
  }
  .subtitle {
    font-size: 14px;
    color: #858B83;
    margin-top: 4px;
  }

  /* Two Column Main Layout */
  .grid-main {
    display: grid;
    grid-template-columns: 1fr 1.35fr;
    gap: 24px;
    margin-bottom: 24px;
  }

  .card {
    background: #FFFFFF;
    border: 1px solid #E8E5DC;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 4px 12px rgba(36, 43, 39, 0.05);
    display: flex;
    flex-direction: column;
  }
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #F0ECE1;
    padding-bottom: 12px;
    margin-bottom: 16px;
  }
  .card-title {
    font-size: 16px;
    font-weight: 800;
    color: #285C45;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* Cost Breakdown List */
  .cost-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
  }
  .cost-item {
    background: #FAF8F5;
    border: 1px solid #E8E5DC;
    border-radius: 10px;
    padding: 12px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .cost-item-labor {
    background: #EAF2ED;
    border-color: #CFE3D5;
  }
  .cost-name {
    font-size: 13px;
    font-weight: 700;
    color: #242B27;
  }
  .cost-sub {
    font-size: 11px;
    color: #858B83;
    margin-top: 2px;
  }
  .cost-val {
    font-size: 16px;
    font-weight: 800;
    color: #242B27;
    text-align: right;
  }
  .cost-pct {
    font-size: 10px;
    font-weight: 700;
    color: #858B83;
  }

  /* Total Base Cost Callout */
  .total-cost-box {
    background: #242B27;
    color: #FFFFFF;
    border-radius: 10px;
    padding: 14px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
  }
  .total-cost-label {
    font-size: 13px;
    font-weight: 700;
  }
  .total-cost-val {
    font-size: 22px;
    font-weight: 800;
    color: #F4C542;
  }

  /* Stacked Bar */
  .bar-container {
    margin-top: 14px;
    margin-bottom: 6px;
  }
  .stacked-bar {
    height: 18px;
    border-radius: 9px;
    display: flex;
    overflow: hidden;
    background: #E8E5DC;
  }
  .bar-clay { width: 21.7%; background: #C47B52; }
  .bar-labor { width: 66.1%; background: #285C45; }
  .bar-pack { width: 5.4%; background: #D69B43; }
  .bar-trans { width: 6.8%; background: #858B83; }

  .bar-legend {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    font-weight: 700;
    color: #636A64;
    margin-top: 6px;
  }

  /* Four Pricing Recommendations */
  .tiers-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }
  .tier-card {
    background: #FAF8F5;
    border: 1px solid #E8E5DC;
    border-radius: 12px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
  }
  .tier-featured {
    background: #FFFFFF;
    border: 2px solid #285C45;
    box-shadow: 0 4px 12px rgba(40,92,69,0.1);
  }
  .tier-badge {
    position: absolute;
    top: 12px;
    right: 12px;
    font-size: 9px;
    font-weight: 800;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 4px;
  }
  .badge-floor { background: #F0EAE1; color: #855A38; }
  .badge-wholesale { background: #FBF0EB; color: #C47B52; }
  .badge-retail { background: #EAF2ED; color: #285C45; }
  .badge-export { background: #EAEBF2; color: #3A4E85; }

  .tier-name {
    font-size: 13px;
    font-weight: 800;
    color: #242B27;
    margin-bottom: 2px;
  }
  .tier-desc {
    font-size: 11px;
    color: #858B83;
    line-height: 1.35;
    margin-bottom: 12px;
  }
  .tier-price {
    font-size: 26px;
    font-weight: 800;
    color: #242B27;
    letter-spacing: -0.5px;
  }
  .tier-margin {
    font-size: 11px;
    font-weight: 700;
    color: #32815A;
    margin-top: 2px;
  }

  /* Bottom Middleman vs Fair Trade Card */
  .benchmark-card {
    background: #FFFFFF;
    border: 1px solid #E8E5DC;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(36,43,39,0.04);
  }
  .benchmark-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #F0ECE1;
    padding-bottom: 10px;
    margin-bottom: 16px;
  }
  .benchmark-title {
    font-size: 14px;
    font-weight: 800;
    color: #285C45;
  }
  .comparison-split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
  .comp-box {
    border-radius: 10px;
    padding: 14px 18px;
    border: 1px solid #E8E5DC;
  }
  .comp-exploitative {
    background: #FFF7F6;
    border-color: #F8D3D0;
  }
  .comp-craftlens {
    background: #F4FAF6;
    border-color: #CFE3D5;
  }
  .comp-heading {
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .comp-details {
    font-size: 12px;
    line-height: 1.5;
    color: #4A524D;
  }
</style>
</head>
<body>

<div class="header">
  <div>
    <div class="fig-tag">Figure 4.5: Explainable Dynamic Pricing Engine Result</div>
    <div class="title">Cost Accounting Breakdown & Four-Tier Market Recommendations</div>
    <div class="subtitle">Detailed breakdown of raw material expenses, living labor wages, logistics overhead, and fair compensation tiers</div>
  </div>
  <div style="background: #FFFFFF; border: 1px solid #E8E5DC; padding: 6px 14px; border-radius: 8px; font-size: 12px; font-weight: 700; color: #285C45;">
    Living Wage Standard: ₹150/hr Minimum Floor
  </div>
</div>

<div class="grid-main">
  <!-- Left: Production Cost Breakdown -->
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        <span>📊 Production Cost Accounting Breakdown</span>
      </div>
      <span style="font-size: 11px; font-weight: 700; color: #858B83;">Base Cost Engine</span>
    </div>

    <div class="cost-list">
      <!-- Raw Materials -->
      <div class="cost-item">
        <div>
          <div class="cost-name">Raw Material Expenses</div>
          <div class="cost-sub">River silt clay, straw husk, organic mineral slip</div>
        </div>
        <div>
          <div class="cost-val">₹320.00</div>
          <div class="cost-pct">21.7% of Base</div>
        </div>
      </div>

      <!-- Artisan Labour -->
      <div class="cost-item cost-item-labor">
        <div>
          <div class="cost-name" style="color: #285C45;">Skilled Artisan Fair Labour</div>
          <div class="cost-sub">6.5 Hours invested @ ₹150/hr living wage rate</div>
        </div>
        <div>
          <div class="cost-val" style="color: #285C45;">₹975.00</div>
          <div class="cost-pct" style="color: #32815A; font-weight: 800;">66.1% (Living Wage Protected)</div>
        </div>
      </div>

      <!-- Packaging -->
      <div class="cost-item">
        <div>
          <div class="cost-name">Packaging & Protective Craft Boxes</div>
          <div class="cost-sub">Eco-friendly corrugated craft packaging & bio tags</div>
        </div>
        <div>
          <div class="cost-val">₹80.00</div>
          <div class="cost-pct">5.4% of Base</div>
        </div>
      </div>

      <!-- Logistics -->
      <div class="cost-item">
        <div>
          <div class="cost-name">Logistics, Kiln Fuel & Overhead</div>
          <div class="cost-sub">Wood fuel, regional cluster dispatch & handling</div>
        </div>
        <div>
          <div class="cost-val">₹100.00</div>
          <div class="cost-pct">6.8% of Base</div>
        </div>
      </div>
    </div>

    <!-- Stacked Cost Proportional Bar -->
    <div class="bar-container">
      <div class="stacked-bar">
        <div class="bar-clay" title="Clay: 21.7%"></div>
        <div class="bar-labor" title="Labor: 66.1%"></div>
        <div class="bar-pack" title="Packaging: 5.4%"></div>
        <div class="bar-trans" title="Transport: 6.8%"></div>
      </div>
      <div class="bar-legend">
        <span>🟫 Raw Materials (21.7%)</span>
        <span style="color: #285C45; font-weight: 800;">🟩 Fair Labor (66.1%)</span>
        <span>🟨 Packaging (5.4%)</span>
        <span>⬛ Transport (6.8%)</span>
      </div>
    </div>

    <!-- Total Break-Even Base -->
    <div class="total-cost-box">
      <div>
        <div class="total-cost-label">Total Production / Break-Even Cost:</div>
        <div style="font-size: 11px; opacity: 0.8; margin-top: 2px;">Direct cost floor — artisan never operates at a loss</div>
      </div>
      <div class="total-cost-val">₹1,475.00</div>
    </div>
  </div>

  <!-- Right: Four Pricing Recommendations -->
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        <span>🏷️ Four Multi-Tier Pricing Recommendations</span>
      </div>
      <span style="font-size: 11px; font-weight: 700; color: #C47B52;">Algorithmic Recommendation</span>
    </div>

    <div class="tiers-grid">
      <!-- Tier 1: Minimum Selling Price -->
      <div class="tier-card">
        <span class="tier-badge badge-floor">Floor Price</span>
        <div>
          <div class="tier-name">1. Minimum Selling Price</div>
          <div class="tier-desc">Absolute break-even threshold. Guarantees 100% fair labor compensation even during clearance or distress sales.</div>
        </div>
        <div>
          <div class="tier-price">₹1,475</div>
          <div class="tier-margin" style="color: #855A38;">0% Profit Margin (100% Wage Safe)</div>
        </div>
      </div>

      <!-- Tier 2: Wholesale Price (B2B Bulk) -->
      <div class="tier-card">
        <span class="tier-badge badge-wholesale">Wholesale B2B</span>
        <div>
          <div class="tier-name">2. Wholesale Price (Bulk)</div>
          <div class="tier-desc">Designed for institutional buyers, retail chains, and cooperatives with minimum batch orders of 25+ units.</div>
        </div>
        <div>
          <div class="tier-price" style="color: #C47B52;">₹1,700</div>
          <div class="tier-margin" style="color: #C47B52;">+15.2% Margin (₹225 Co-op Profit)</div>
        </div>
      </div>

      <!-- Tier 3: Recommended Retail Price (B2C) -->
      <div class="tier-card tier-featured">
        <span class="tier-badge badge-retail">Recommended B2C</span>
        <div>
          <div class="tier-name" style="color: #285C45;">3. Recommended Retail Price</div>
          <div class="tier-desc">Direct-to-consumer online store pricing. Provides optimal balance of consumer demand and maximum artisan profit.</div>
        </div>
        <div>
          <div class="tier-price" style="color: #285C45;">₹1,850</div>
          <div class="tier-margin" style="color: #32815A;">+25.4% Margin (₹375 Direct Profit)</div>
        </div>
      </div>

      <!-- Tier 4: Premium / Export Price -->
      <div class="tier-card">
        <span class="tier-badge badge-export">Global Export</span>
        <div>
          <div class="tier-name">4. Premium / Export Price</div>
          <div class="tier-desc">International conscious consumer pricing. Incorporates export packaging, GI provenance tag, and customs clearance.</div>
        </div>
        <div>
          <div class="tier-price" style="color: #3A4E85;">₹2,680</div>
          <div class="tier-margin" style="color: #3A4E85;">+81.7% Margin (Global Market Tier)</div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Bottom: Market Benchmark Comparison -->
<div class="benchmark-card">
  <div class="benchmark-header">
    <div class="benchmark-title">
      <span>⚖️ Market Benchmark & Value Distribution Analysis: Middleman vs. CraftLens</span>
    </div>
    <span style="font-size: 11px; font-weight: 700; color: #285C45;">Verified by Market Index (/api/v1/pricing/calculate)</span>
  </div>

  <div class="comparison-split">
    <!-- Conventional Middleman Model -->
    <div class="comp-box comp-exploitative">
      <div class="comp-heading" style="color: #C6534B;">
        <span>❌ Conventional Handicraft Middleman Supply Chain</span>
      </div>
      <div class="comp-details">
        • <strong>Retail Shelf Price:</strong> ₹2,400 to ₹3,200 in urban city boutiques.<br>
        • <strong>Artisan Receives:</strong> Only <strong>₹350 – ₹420 (14% - 17%)</strong>, well below minimum daily living wages.<br>
        • <strong>Exploitation Factor:</strong> Wholesalers, traders, and intermediaries capture <strong>83% to 86%</strong> of value creation without making or sculpting the craft.
      </div>
    </div>

    <!-- CraftLens Fair-Wage Model -->
    <div class="comp-box comp-craftlens">
      <div class="comp-heading" style="color: #285C45;">
        <span>✓ CraftLens 2.0 Direct Ethical Pricing Model</span>
      </div>
      <div class="comp-details">
        • <strong>Fair Retail Price:</strong> <strong>₹1,850</strong> (Substantially more affordable for conscious consumers).<br>
        • <strong>Artisan Receives:</strong> <strong>₹1,350 (73.0% of total retail price)</strong> directly transferred to artisan bank accounts.<br>
        • <strong>Living Wage Guaranteed:</strong> Protects ₹150/hr labor compensation plus ₹375 net profit per craft piece.
      </div>
    </div>
  </div>
</div>

</body>
</html>
"""

with open("photos/fig_4_5.html", "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_img = r"D:\projects\KD\SIH26090\photos\Figure_4.5_Pricing_Calculator_Result.png"

args = [
    chrome_path,
    "--headless=new",
    "--no-sandbox",
    "--disable-gpu",
    "--window-size=1400,920",
    f"--screenshot={out_img}",
    "file:///D:/projects/KD/SIH26090/photos/fig_4_5.html"
]

res = subprocess.run(args, capture_output=True, text=True)
print("Return code:", res.returncode)
print("File exists:", os.path.exists(out_img))
if os.path.exists(out_img):
    print("File size:", os.path.getsize(out_img), "bytes")


const paymentFields = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"];
const billFields = ["BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6"];
const payAmountFields = ["PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"];
const monthLabels = ["Son Ay", "2 Ay Önce", "3 Ay Önce", "4 Ay Önce", "5 Ay Önce", "6 Ay Önce"];
const defaultBills = [50000, 48000, 47000, 45000, 43000, 42000];
const defaultPays = [5000, 5000, 5000, 5000, 5000, 5000];

function buildDynamicFields() {
  const statusGrid = document.getElementById("payment-status-grid");
  const billGrid = document.getElementById("bill-grid");
  const payGrid = document.getElementById("pay-grid");

  const statusOptions = [
    [-2, "-2 — Hesap hareketi yok"], [-1, "-1 — Zamanında ödeme"], [0, "0 — Gecikme yok"],
    [1, "1 — 1 ay gecikme"], [2, "2 — 2 ay gecikme"], [3, "3 — 3 ay gecikme"],
    [4, "4 — 4 ay gecikme"], [5, "5 — 5 ay gecikme"], [6, "6 — 6 ay gecikme"],
    [7, "7 — 7 ay gecikme"], [8, "8 — 8 ay gecikme"], [9, "9 — 9+ ay gecikme"]
  ];

  paymentFields.forEach((name, idx) => {
    const wrapper = document.createElement("div");
    wrapper.className = "payment-status-item";
    const label = document.createElement("label");
    label.textContent = monthLabels[idx];
    const select = document.createElement("select");
    select.name = name;
    select.required = true;
    statusOptions.forEach(([value, text]) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = text;
      if (value === 0) option.selected = true;
      select.appendChild(option);
    });
    wrapper.append(label, select);
    statusGrid.appendChild(wrapper);
  });

  billFields.forEach((name, idx) => billGrid.appendChild(amountField(name, monthLabels[idx], defaultBills[idx], false)));
  payAmountFields.forEach((name, idx) => payGrid.appendChild(amountField(name, monthLabels[idx], defaultPays[idx], true)));
}

function amountField(name, labelText, value, nonNegative) {
  const wrapper = document.createElement("div");
  wrapper.className = "amount-item";
  const label = document.createElement("label");
  label.textContent = labelText;
  const input = document.createElement("input");
  input.type = "number";
  input.name = name;
  input.value = value;
  input.step = "100";
  if (nonNegative) input.min = "0";
  input.required = true;
  wrapper.append(label, input);
  return wrapper;
}

function collectPayload() {
  const form = document.getElementById("risk-form");
  const data = new FormData(form);
  const payload = {};
  for (const [key, value] of data.entries()) payload[key] = Number(value);
  return payload;
}

function formatMoney(value) {
  return new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 0 }).format(value) + " NT$";
}

function computeSummaries(payload) {
  const billSum = billFields.reduce((sum, key) => sum + (payload[key] || 0), 0);
  const paySum = payAmountFields.reduce((sum, key) => sum + (payload[key] || 0), 0);
  const ratio = payload.LIMIT_BAL / Math.max(paySum, 1);
  document.getElementById("bill-sum").textContent = formatMoney(billSum);
  document.getElementById("pay-sum").textContent = formatMoney(paySum);
  document.getElementById("limit-per-pay").textContent = ratio.toLocaleString("tr-TR", { maximumFractionDigits: 2 }) + "x";
  drawTrendChart(billFields.map(k => payload[k]), payAmountFields.map(k => payload[k]));
}

function riskBand(probability, threshold) {
  if (probability >= threshold) return "high";
  if (probability >= threshold * 0.55) return "medium";
  return "low";
}

function updateResult(result) {
  const p = Math.max(0, Math.min(1, result.default_probability));
  const percentage = p * 100;
  const band = riskBand(p, result.threshold);
  const badge = document.getElementById("risk-badge");
  const gauge = document.getElementById("risk-gauge");
  const decision = document.getElementById("decision-panel");

  document.getElementById("risk-percentage").textContent = percentage.toLocaleString("tr-TR", { maximumFractionDigits: 1 }) + "%";
  document.getElementById("threshold-value").textContent = (result.threshold * 100).toLocaleString("tr-TR", { maximumFractionDigits: 1 }) + "%";
  document.getElementById("threshold-marker").style.left = `${result.threshold * 100}%`;
  document.getElementById("probability-fill").style.width = `${percentage}%`;

  gauge.style.setProperty("--risk", `${p * 360}deg`);
  const colors = { low: "#159a6b", medium: "#db8b13", high: "#d94d55" };
  gauge.style.setProperty("--gauge-color", colors[band]);

  badge.className = `risk-badge ${band}`;
  badge.textContent = band === "low" ? "Düşük Risk" : band === "medium" ? "Orta Risk" : "Yüksek Risk";

  decision.className = `decision-panel ${band}`;
  if (result.prediction === 1) {
    decision.innerHTML = `<span class="decision-icon">!</span><div><strong>Temerrüt riski eşik üzerinde</strong><p>Model olasılığı karar eşiğini geçti. Daha ayrıntılı kredi incelemesi önerilir.</p></div>`;
  } else if (band === "medium") {
    decision.innerHTML = `<span class="decision-icon">~</span><div><strong>Eşiğe yakın risk profili</strong><p>Tahmin temerrüt sınıfında değil, ancak olasılık karar eşiğine yaklaşıyor.</p></div>`;
  } else {
    decision.innerHTML = `<span class="decision-icon">✓</span><div><strong>Temerrüt riski eşik altında</strong><p>Mevcut girdilerle model düşük risk sinyali üretmiştir.</p></div>`;
  }
}

function drawTrendChart(bills, pays) {
  const canvas = document.getElementById("trend-chart");
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(600, rect.width * ratio);
  canvas.height = 300 * ratio;
  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);
  const width = canvas.width / ratio;
  const height = canvas.height / ratio;
  ctx.clearRect(0, 0, width, height);

  const pad = { left: 42, right: 14, top: 15, bottom: 34 };
  const chartW = width - pad.left - pad.right;
  const chartH = height - pad.top - pad.bottom;
  const max = Math.max(...bills.map(Math.abs), ...pays.map(Math.abs), 1) * 1.15;

  ctx.strokeStyle = "#e7ecf3";
  ctx.lineWidth = 1;
  ctx.font = "9px Inter, sans-serif";
  ctx.fillStyle = "#8793a5";
  ctx.textAlign = "right";
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + chartH * (i / 4);
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(width - pad.right, y); ctx.stroke();
    const value = max * (1 - i / 4);
    ctx.fillText(value >= 1000 ? `${Math.round(value / 1000)}k` : Math.round(value), pad.left - 7, y + 3);
  }

  const groupW = chartW / 6;
  const barW = Math.min(20, groupW * .28);
  monthLabels.forEach((label, i) => {
    const center = pad.left + groupW * i + groupW / 2;
    const billH = Math.max(0, bills[i]) / max * chartH;
    const payH = Math.max(0, pays[i]) / max * chartH;
    ctx.fillStyle = "#2d72e8";
    roundedRect(ctx, center - barW - 2, pad.top + chartH - billH, barW, billH, 3);
    ctx.fill();
    ctx.fillStyle = "#29a57b";
    roundedRect(ctx, center + 2, pad.top + chartH - payH, barW, payH, 3);
    ctx.fill();
    ctx.fillStyle = "#7d899a";
    ctx.textAlign = "center";
    ctx.fillText(`${i + 1}. Ay`, center, height - 12);
  });
}

function roundedRect(ctx, x, y, width, height, radius) {
  const r = Math.min(radius, Math.abs(width) / 2, Math.abs(height) / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + width, y, x + width, y + height, r);
  ctx.arcTo(x + width, y + height, x, y + height, r);
  ctx.arcTo(x, y + height, x, y, r);
  ctx.arcTo(x, y, x + width, y, r);
  ctx.closePath();
}

async function handleSubmit(event) {
  event.preventDefault();
  const button = document.getElementById("predict-button");
  const error = document.getElementById("form-error");
  const payload = collectPayload();
  error.classList.remove("show");
  button.disabled = true;
  button.classList.add("loading");
  button.querySelector(".button-label").textContent = "Model hesaplıyor...";
  computeSummaries(payload);

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Tahmin isteği başarısız oldu.");
    updateResult(data);
  } catch (err) {
    error.textContent = err.message || "Beklenmeyen bir hata oluştu.";
    error.classList.add("show");
  } finally {
    button.disabled = false;
    button.classList.remove("loading");
    button.querySelector(".button-label").textContent = "Temerrüt Riskini Hesapla";
  }
}

function resetForm() {
  const form = document.getElementById("risk-form");
  form.reset();
  const payload = collectPayload();
  computeSummaries(payload);
  document.getElementById("risk-percentage").textContent = "—";
  const gauge = document.getElementById("risk-gauge");
  gauge.style.setProperty("--risk", "0deg");
  gauge.style.setProperty("--gauge-color", "#d9e1eb");
  document.getElementById("probability-fill").style.width = "0%";
  const badge = document.getElementById("risk-badge");
  badge.className = "risk-badge neutral";
  badge.textContent = "Henüz hesaplanmadı";
  const decision = document.getElementById("decision-panel");
  decision.className = "decision-panel";
  decision.innerHTML = `<span class="decision-icon">✓</span><div><strong>Değerlendirmeye hazır</strong><p>Formu doldurup tahmin butonuna basın.</p></div>`;
}

function initNavigation() {
  document.querySelectorAll("button.nav-item[data-view]").forEach(button => {
    button.addEventListener("click", () => {
      document.querySelectorAll("button.nav-item[data-view]").forEach(b => b.classList.remove("active"));
      button.classList.add("active");
      document.querySelectorAll(".view").forEach(view => view.classList.remove("active-view"));
      document.getElementById(button.dataset.view).classList.add("active-view");
      document.getElementById("page-title").textContent = button.dataset.view === "prediction-view" ? "Müşteri Temerrüt Riski" : "Model Performansı";
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });
}

buildDynamicFields();
initNavigation();
document.getElementById("risk-form").addEventListener("submit", handleSubmit);
document.getElementById("reset-form").addEventListener("click", resetForm);
computeSummaries(collectPayload());
window.addEventListener("resize", () => computeSummaries(collectPayload()));

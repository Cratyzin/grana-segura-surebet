
const btn = document.getElementById("calc-btn");
const resultCard = document.getElementById("result");
const arbPercentEl = document.getElementById("arb-percent");
const lucroLiquidoEl = document.getElementById("lucro-liquido");
const lucroPercentualEl = document.getElementById("lucro-percentual");
const betsListEl = document.getElementById("bets-list");
const legendaEl = document.getElementById("legenda");
const winAudio = document.getElementById("win-audio");

async function calcular() {
  const odd1 = parseFloat(document.getElementById("odd1").value);
  const odd2 = parseFloat(document.getElementById("odd2").value);
  const odd3 = parseFloat(document.getElementById("odd3").value);
  const stake = parseFloat(document.getElementById("stake").value);

  const odds = [odd1, odd2, odd3].filter((v) => !isNaN(v) && v > 1);

  if (odds.length < 2 || isNaN(stake) || stake <= 0) {
    alert("Preencha pelo menos 2 odds válidas e o valor da stake.");
    return;
  }

  const payload = { odds, stake };

  try {
    const resp = await fetch("/grana-segura", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      const err = await resp.json();
      alert(err.detail || "Erro ao calcular");
      return;
    }
    const data = await resp.json();
    renderResultado(data);
  } catch (err) {
    console.error(err);
    alert("Erro de conexão com o servidor.");
  }
}

function renderResultado(data) {
  resultCard.classList.remove("hidden");
  arbPercentEl.textContent = data.arb_percent + " %";
  lucroLiquidoEl.textContent = "R$ " + data.lucro_liquido.toFixed(2);
  lucroPercentualEl.textContent = data.lucro_percentual + " %";

  betsListEl.innerHTML = "";
  data.bets.forEach((b, i) => {
    const li = document.createElement("li");
    li.innerHTML = `<span>Casa ${i + 1} (odd ${data.odds[i]})</span><strong>R$ ${b.toFixed(2)}</strong>`;
    betsListEl.appendChild(li);
  });

  if (data.is_surebet) {
    legendaEl.textContent = "✅ Surebet detectada! Distribuição feita para lucro garantido.";
    try { winAudio.play(); } catch (e) {}
  } else {
    legendaEl.textContent = "⚠️ Não é uma surebet perfeita (soma das probabilidades ≥ 100%).";
  }
}

btn.addEventListener("click", calcular);

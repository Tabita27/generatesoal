const API_BASE = "http://localhost:8000/api";

let currentText = "";
let currentQuestions = [];

// ─── Upload Handler ───────────────────────────────────────────────

async function handleFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  await uploadFile(file);
}

function handleDrop(event) {
  event.preventDefault();
  const file = event.dataTransfer.files[0];
  if (file) uploadFile(file);
}

async function uploadFile(file) {
  const status = document.getElementById("file-status");
  status.textContent = `⏳ Mengekstrak teks dari ${file.name}...`;
  status.classList.remove("hidden");

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/upload/`, {
      method: "POST",
      body: formData
    });
    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || "Gagal mengunggah file");

    currentText = data.text;
    document.getElementById("manual-text").value = data.text;
    status.textContent = `✅ ${file.name} — ${data.word_count} kata terdeteksi`;
  } catch (err) {
    status.textContent = `❌ ${err.message}`;
  }
}

function showToast(message, type = "warning") {

  const container =
    document.getElementById("toast-container");

  const colors = {
    success: "border-green-500 bg-green-50 text-green-700",
    error: "border-red-500 bg-red-50 text-red-700",
    warning: "border-yellow-500 bg-yellow-50 text-yellow-700",
    info: "border-blue-500 bg-blue-50 text-blue-700"
  };

  const icons = {
    success: "✅",
    error: "❌",
    warning: "⚠️",
    info: "ℹ️"
  };

  const toast = document.createElement("div");

  toast.className = `
    min-w-[320px]
    max-w-[400px]
    px-4
    py-3
    rounded-xl
    border-l-4
    shadow-lg
    backdrop-blur
    animate-toast-in
    ${colors[type]}
  `;

  toast.innerHTML = `
    <div class="flex items-start gap-3">
      <div class="text-lg">
        ${icons[type]}
      </div>

      <div class="text-sm font-medium">
        ${message}
      </div>
    </div>
  `;

  container.appendChild(toast);

  setTimeout(() => {

    toast.classList.add("animate-toast-out");

    setTimeout(() => {
      toast.remove();
    }, 300);

  }, 3000);
}
// ─── Generate Soal ───────────────────────────────────────────────

async function generateSoal() {
  const teks = document.getElementById("manual-text").value.trim();
  const errorBox =
    document.getElementById("upload-error");

  if (!teks) {

  showToast(
    "Silakan unggah atau tempel materi pembelajaran terlebih dahulu.",
    "warning"
  );

  return;
}

errorBox.classList.add("hidden");

  const btn = document.getElementById("btn-generate");
  btn.disabled = true;
  btn.textContent = "⏳ Sedang membuat soal...";

  const payload = {
    text: teks,
    question_type: document.getElementById("tipe-soal").value,
    jumlah_soal: parseInt(document.getElementById("jumlah-soal").value),
    tingkat_kesulitan: document.getElementById("kesulitan").value
  };

  try {
    const res = await fetch(`${API_BASE}/generate/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Gagal menghasilkan soal");

    currentText = teks;
    currentQuestions = data.questions;

    renderKeywords(data.keywords);
    renderQuestions(data.questions);

    document.getElementById("hasil-section").classList.remove("hidden");
    document.getElementById("hasil-section").scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "✨ Buat Soal Otomatis";
  }
}

// ─── Render Keywords ─────────────────────────────────────────────

function renderKeywords(keywords) {
  const container = document.getElementById("keywords-container");
  const section = document.getElementById("keywords-section");

  if (!container || !section) {
    return;
  }

  container.innerHTML = keywords.map(kw => `
    <span class="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">${kw}</span>
  `).join("");

  section.classList.remove("hidden");
}

// ─── Render Questions ─────────────────────────────────────────────

function renderQuestions(questions) {
  const container = document.getElementById("questions-container");

  const badgeColor = {
    mudah: "bg-green-100 text-green-800",
    sedang: "bg-yellow-100 text-yellow-800",
    sulit: "bg-red-100 text-red-800"
  };

  container.innerHTML = questions.map((q, i) => {
    const pilihan = q.pilihan && typeof q.pilihan === "object"
      ? Object.entries(q.pilihan)
      : [];

    const pilihanHTML = pilihan.length > 0
      ? `<div class="mt-3 space-y-1">
          ${pilihan.map(([huruf, isi]) => {
            const isKunci = huruf === q.kunci_jawaban;
            return `<div class="flex items-start gap-2 text-sm ${isKunci ? "text-green-700 font-semibold" : "text-gray-700"}">
              <span class="w-5 shrink-0">${huruf}.</span>
              <span>${isi} ${isKunci ? "✓" : ""}</span>
            </div>`;
          }).join("")}
        </div>`
      : `<p class="mt-3 text-sm text-green-700 font-semibold">✓ Jawaban: ${q.kunci_jawaban}</p>`;

    const difficulty = badgeColor[q.tingkat_kesulitan] || "bg-gray-100 text-gray-700";

    return `
      <div class="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 transition" id="q-${i}">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-semibold text-gray-700">Soal ${q.nomor}</span>
          <div class="flex gap-2">
            <span class="text-xs px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">
              ${q.tipe === "pilihan_ganda" ? "Pilihan Ganda" : "Isian"}
            </span>
            <span class="text-xs px-2 py-0.5 rounded-full ${difficulty}">
              ${q.tingkat_kesulitan}
            </span>
          </div>
        </div>
        <p class="text-sm text-gray-800">${q.pertanyaan}</p>
        ${pilihanHTML}
        <div class="mt-3 flex gap-2">
          <button onclick="editSoal(${i})" class="text-xs text-indigo-600 hover:underline">✏ Edit</button>
          <button onclick="hapusSoal(${i})" class="text-xs text-red-500 hover:underline">🗑 Hapus</button>
        </div>
      </div>
    `;
  }).join("");
}

// ─── Edit & Hapus ─────────────────────────────────────────────────

function editSoal(index) {
  const q = currentQuestions[index];
  const pertanyaanBaru = prompt("Edit pertanyaan:", q.pertanyaan);
  if (pertanyaanBaru !== null) {
    currentQuestions[index].pertanyaan = pertanyaanBaru;
    renderQuestions(currentQuestions);
  }
}

function hapusSoal(index) {
  if (confirm("Hapus soal ini?")) {
    currentQuestions.splice(index, 1);
    currentQuestions.forEach((q, i) => q.nomor = i + 1);
    renderQuestions(currentQuestions);
  }
}

// ─── Export ───────────────────────────────────────────────────────

async function exportSoal(format) {
  if (currentQuestions.length === 0) {
    alert("Tidak ada soal untuk diekspor.");
    return;
  }

  const judul = prompt("Judul dokumen soal:", "Soal Latihan") || "Soal Latihan";

  const payload = {
    judul: judul,
    questions: currentQuestions,
    format: format
  };

  try {
    const res = await fetch(`${API_BASE}/export/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error("Gagal mengekspor");

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${judul}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    alert(`Error export: ${err.message}`);
  }
}
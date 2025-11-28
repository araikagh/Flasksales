const form = document.getElementById("product-form");
const statusP = document.getElementById("status");
const responseBox = document.getElementById("response-box");

form?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    ProductName: document.getElementById("ProductName").value,
    Manufacturer: document.getElementById("Manufacturer").value,
    ProductCount: parseInt(document.getElementById("ProductCount").value),
    Price: parseFloat(document.getElementById("Price").value)
  };

  try {
    const res = await fetch("/api/products", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    responseBox.textContent = JSON.stringify(data, null, 2);

    if (res.ok && data.ok) {
      statusP.className = "ok";
      statusP.textContent = data.message || "OK";
      form.reset();
    } else {
      statusP.className = "err";
      statusP.textContent = "Ошибка: " + (data.message || JSON.stringify(data.errors));
    }
  } catch (err) {
    statusP.className = "err";
    statusP.textContent = "Ошибка сети / Network error";
    responseBox.textContent = String(err);
  }
});

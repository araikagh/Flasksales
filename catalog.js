(async function(){
  const productsGrid = document.getElementById("products-grid");
  const categoriesDiv = document.getElementById("categories");
  const searchInput = document.getElementById("search-input");
  const searchBtn = document.getElementById("search-btn");
  const resetBtn = document.getElementById("reset-btn");
  const statsDiv = document.getElementById("stats");

  let products = [];
  let categories = [];

  async function loadStats(){
    const r = await fetch("/api/stats");
    const j = await r.json();
    if(j.ok){
      statsDiv.innerHTML = `
        <div class="stat-card">Заказы: <b>${j.total_orders}</b></div>
        <div class="stat-card">Клиенты: <b>${j.total_customers}</b></div>
        <div class="stat-card">Товары: <b>${j.total_products}</b></div>
        <div class="stat-card">Продажи: <b>${j.total_sales}</b></div>
      `;
    }
  }

  async function loadCategories(){
    const res = await fetch("/api/categories/");
    categories = await res.json();
    categoriesDiv.innerHTML = `<button class="category-btn" data-id="">Все</button>` + categories.map(c=>`<button class="category-btn" data-id="${c.id}">${c.CategoryName}</button>`).join("");
    categoriesDiv.querySelectorAll(".category-btn").forEach(b=>{
      b.addEventListener("click", ()=>{ const id = b.dataset.id; if(id) filterByCategory(id); else renderProducts(products); });
    });
  }

  async function loadProducts(){
    const res = await fetch("/api/products/");
    products = await res.json();
    renderProducts(products);
  }

  function renderProducts(list){
    productsGrid.innerHTML = "";
    list.forEach(p=>{
      const el = document.createElement("div");
      el.className = "product-card";
      el.innerHTML = `
        <h3>${p.ProductName}</h3>
        <div class="meta">Производитель: ${p.Manufacturer || "-"}</div>
        <div class="meta">Категория: ${p.CategoryName || "-"}</div>
        <div class="meta">В наличии: <b>${p.ProductCount}</b></div>
        <div class="meta buy">
          <div class="price">${p.Price} </div>
          <div>
            <input type="number" min="1" max="${p.ProductCount}" value="1" id="cnt-${p.id}" />
            <button class="btn btn-primary buy-btn" data-id="${p.id}" data-max="${p.ProductCount}">Купить</button>
          </div>
        </div>
      `;
      productsGrid.appendChild(el);
    });
    // attach buy handlers
    productsGrid.querySelectorAll(".buy-btn").forEach(btn=>{
      btn.addEventListener("click", async ()=> {
        const pid = btn.dataset.id;
        const cnt = Number(document.getElementById(`cnt-${pid}`).value || 1);
        const res = await fetch("/api/orders/", {
          method: "POST",
          headers: {"Content-Type":"application/json"},
          body: JSON.stringify({ ProductId: Number(pid), ProductCount: cnt })
        });
        const j = await res.json();
        if(res.ok && j.ok){
          alert("Заказ создан!");
          await loadProducts();
          await loadStats();
        } else {
          alert("Ошибка: " + (j.message || JSON.stringify(j)));
        }
      });
    });
  }

  function filterByCategory(id){
    fetch(`/api/products/?category=${id}`).then(r=>r.json()).then(data=>renderProducts(data));
  }

  searchBtn.addEventListener("click", ()=> {
    const q = searchInput.value.trim();
    if(!q) return loadProducts();
    fetch(`/api/products/?q=${encodeURIComponent(q)}`).then(r=>r.json()).then(data=>renderProducts(data));
  });
  resetBtn.addEventListener("click", ()=> { searchInput.value=""; loadProducts(); });

  // init
  await loadStats();
  await loadCategories();
  await loadProducts();
})();

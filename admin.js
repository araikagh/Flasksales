document.addEventListener("DOMContentLoaded", () => {
  const holder = document.getElementById("table-holder");
  const statsEl = document.getElementById("admin-stats");

  async function loadStats(){
    const res = await fetch("/api/stats");
    const j = await res.json();
    if(j.ok){
      statsEl.innerHTML = `
        <div class="stat-card">Заказы: <b>${j.total_orders}</b></div>
        <div class="stat-card">Клиенты: <b>${j.total_customers}</b></div>
        <div class="stat-card">Товары: <b>${j.total_products}</b></div>
        <div class="stat-card">Продажи: <b>${j.total_sales}</b></div>
      `;
    }
  }

  document.querySelectorAll("[data-table]").forEach(btn=>{
    btn.addEventListener("click", ()=>openTable(btn.dataset.table));
  });

  let currentTabulator = null;

  async function openTable(table){
    holder.innerHTML = "<div class='card'>Загрузка...</div>";
    try {
      const res = await fetch(`/api/${table}/`);
      const data = await res.json();
      if(!Array.isArray(data)){
        holder.innerHTML = "<div class='card'>Нет данных</div>";
        return;
      }
      if(currentTabulator){
        currentTabulator.destroy();
        currentTabulator = null;
      }
      holder.innerHTML = "<div id='tabulator-table'></div>";

      const sample = data[0] || {};
      const cols = Object.keys(sample).map(k=>{
        const isId = /id/i.test(k) && (k.toLowerCase().includes("id") || k.toLowerCase().includes("order"));
        return {
          title: k,
          field: k,
          editor: isId ? false : "input",
          headerFilter: "input"
        };
      });

      if(table === "products" && !cols.find(c=>c.field === "CategoryName")){
        cols.push({title:"CategoryName", field:"CategoryName", editor:false, headerFilter:"input"});
      }

      cols.push({
        title:"Actions",
        headerSort:false,
        formatter:function(cell, formatterParams){
          return "<button class='btn btn-primary btn-save'>Save</button> <button class='btn btn-ghost btn-del'>Del</button>";
        },
        width:160,
        hozAlign:"center",
        cellClick:function(e, cell){
          const row = cell.getRow();
          const tgt = e.target;
          const rowdata = row.getData();
          if(tgt.classList.contains("btn-save")){
            saveRow(table, rowdata);
          } else if(tgt.classList.contains("btn-del")){
            deleteRow(table, rowdata);
          }
        }
      });

      currentTabulator = new Tabulator("#tabulator-table", {
        data: data,
        layout:"fitColumns",
        columns: cols,
        pagination:"local",
        paginationSize:25,
        movableColumns:true,
      });

      const createForm = document.createElement("div");
      createForm.className = "card";
      createForm.style.marginTop = "12px";
      createForm.innerHTML = `<h3>Добавить новую запись в ${table}</h3>`;

      if(table === "products"){
        const catsRes = await fetch("/api/categories/");
        const categories = await catsRes.json();
        createForm.innerHTML += `
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <input id="new-ProductName" placeholder="ProductName" />
            <input id="new-Manufacturer" placeholder="Manufacturer" />
            <input id="new-ProductCount" type="number" placeholder="ProductCount" />
            <input id="new-Price" type="number" step="0.01" placeholder="Price" />
            <select id="new-CategoryId"></select>
            <button id="create-btn" class="btn btn-primary">Добавить товар</button>
          </div>
        `;
        setTimeout(()=>{
          const select = document.getElementById("new-CategoryId");
          select.innerHTML = `<option value="">--Выбрать категорию--</option>` + categories.map(c=>`<option value="${c.id}">${c.CategoryName}</option>`).join("");
        }, 0);

      } else if(table === "customers"){
        createForm.innerHTML += `<div><input id="new-FirstName" placeholder="FirstName" /> <button id="create-btn" class="btn btn-primary">Добавить клиента</button></div>`;
      } else if(table === "categories"){
        createForm.innerHTML += `<div><input id="new-CategoryName" placeholder="CategoryName" /> <button id="create-btn" class="btn btn-primary">Добавить категорию</button></div>`;
      } else if(table === "orders"){
        const customersRes = await fetch("/api/customers/");
        const customers = await customersRes.json();
        const productsRes = await fetch("/api/products/");
        const products = await productsRes.json();
        createForm.innerHTML += `
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <select id="new-CustomerId">${customers.map(c=>`<option value="${c.idCustomers}">${c.FirstName}</option>`).join("")}</select>
            <select id="new-ProductId">${products.map(p=>`<option value="${p.id}">${p.ProductName}</option>`).join("")}</select>
            <input id="new-ProductCount" type="number" placeholder="ProductCount" value="1" />
            <button id="create-btn" class="btn btn-primary">Добавить заказ</button>
          </div>
        `;
      }

      holder.appendChild(createForm);

      const btn = document.getElementById("create-btn");
      if(btn){
        btn.addEventListener("click", async ()=>{
          try {
            let payload = {};
            if(table === "products"){
              payload = {
                ProductName: document.getElementById("new-ProductName").value,
                Manufacturer: document.getElementById("new-Manufacturer").value,
                ProductCount: Number(document.getElementById("new-ProductCount").value || 0),
                Price: Number(document.getElementById("new-Price").value || 0),
                CategoryId: Number(document.getElementById("new-CategoryId").value || 0)
              };
            } else if(table === "customers"){
              payload = { FirstName: document.getElementById("new-FirstName").value };
            } else if(table === "categories"){
              payload = { CategoryName: document.getElementById("new-CategoryName").value };
            } else if(table === "orders"){
              payload = {
                CustomerId: Number(document.getElementById("new-CustomerId").value),
                ProductId: Number(document.getElementById("new-ProductId").value),
                ProductCount: Number(document.getElementById("new-ProductCount").value)
              };
            }
            const resp = await fetch(`/api/${table}/`, {
              method: "POST",
              headers: {"Content-Type":"application/json"},
              body: JSON.stringify(payload)
            });
            const j = await resp.json();
            if(!resp.ok) throw new Error(j.message || "Ошибка");
            alert("Создано");
            openTable(table);
            loadStats();
          } catch(e){
            alert("Ошибка при создании: " + e.message);
          }
        });
      }

    } catch(err){
      holder.innerHTML = `<div class="card">Ошибка: ${err.message}</div>`;
    }
  }

  async function saveRow(table, rowdata){
    const idKey = Object.keys(rowdata).find(k=>/id/i.test(k));
    const id = rowdata[idKey];
    const payload = {...rowdata};
    delete payload[idKey];
    try {
      const resp = await fetch(`/api/${table}/${id}`, {
        method: "PUT",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify(payload)
      });
      const j = await resp.json();
      if(!resp.ok) throw new Error(j.message || "Ошибка при сохранении");
      alert("Сохранено");
      openTable(table);
      loadStats();
    } catch(e){
      alert("Ошибка: " + e.message);
    }
  }

  async function deleteRow(table, rowdata){
    if(!confirm("Удалить запись?")) return;
    const idKey = Object.keys(rowdata).find(k=>/id/i.test(k));
    const id = rowdata[idKey];
    try {
      const resp = await fetch(`/api/${table}/${id}`, { method: "DELETE" });
      const j = await resp.json();
      if(!resp.ok) throw new Error(j.message || "Ошибка при удалении");
      alert("Удалено");
      openTable(table);
      loadStats();
    } catch(e){
      alert("Ошибка: " + e.message);
    }
  }

  loadStats();
});

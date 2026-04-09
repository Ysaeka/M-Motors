const tabLocation = document.getElementById("tab-location");
const tabAchat = document.getElementById("tab-achat");
const priceSelect = document.getElementById("price-select");
const searchBox = document.getElementById("search-box");

function setLocationMode() {
  tabLocation.classList.add("active");
  tabAchat.classList.remove("active");
  searchBox.classList.remove("mode-achat");

  priceSelect.innerHTML = `
    <option selected>Mensualité</option>
    <option>200 € / mois</option>
    <option>300 € / mois</option>
    <option>400 € / mois</option>
  `;
}

function setAchatMode() {
  tabAchat.classList.add("active");
  tabLocation.classList.remove("active");
  searchBox.classList.add("mode-achat");

  priceSelect.innerHTML = `
    <option selected>Budget</option>
    <option>10 000 €</option>
    <option>15 000 €</option>
    <option>20 000 €</option>
  `;
}

tabLocation.addEventListener("click", setLocationMode);
tabAchat.addEventListener("click", setAchatMode);
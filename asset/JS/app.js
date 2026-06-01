document.addEventListener("DOMContentLoaded", function () {
  /*
   * Home page search tabs
   * Location / Achat switch
   */
  const tabLocation = document.getElementById("tab-location");
  const tabAchat = document.getElementById("tab-achat");
  const priceSelect = document.getElementById("price-select");
  const searchBox = document.getElementById("search-box");
  const homeOfferType = document.getElementById("home-offer-type");

  if (tabLocation && tabAchat && priceSelect && searchBox && homeOfferType) {
    function setLocationMode() {
      homeOfferType.value = "lld";

      tabLocation.classList.add("active");
      tabAchat.classList.remove("active");
      searchBox.classList.remove("mode-achat");

      priceSelect.innerHTML = `
        <option value="" selected>Mensualité</option>
        <option value="200">200 € / mois</option>
        <option value="300">300 € / mois</option>
        <option value="400">400 € / mois</option>
      `;
    }

    function setAchatMode() {
      homeOfferType.value = "sale";

      tabAchat.classList.add("active");
      tabLocation.classList.remove("active");
      searchBox.classList.add("mode-achat");

      priceSelect.innerHTML = `
        <option value="" selected>Budget</option>
        <option value="10000">10 000 €</option>
        <option value="15000">15 000 €</option>
        <option value="20000">20 000 €</option>
      `;
    }
    tabLocation.addEventListener("click", setLocationMode);
    tabAchat.addEventListener("click", setAchatMode);
  }

  /*
   * Catalog automatic filters
   */
  const catalogFilterForm = document.getElementById("catalog-filter-form");

  if (catalogFilterForm) {
    const instantFields = catalogFilterForm.querySelectorAll(
      "select, input[type='checkbox']"
    );
    const budgetRange = catalogFilterForm.querySelector("input[type='range']");
    const budgetValue = document.getElementById("budgetValue");

    function formatBudgetValue() {
      if (!budgetRange || !budgetValue) {
        return;
      }

      budgetValue.textContent =
        new Intl.NumberFormat("fr-FR").format(budgetRange.value) + " €";
    }

    formatBudgetValue();

    instantFields.forEach(function (field) {
      field.addEventListener("change", function () {
        catalogFilterForm.submit();
      });
    });

    if (budgetRange) {
      budgetRange.addEventListener("input", formatBudgetValue);

      budgetRange.addEventListener("change", function () {
        catalogFilterForm.submit();
      });
    }
  }
});
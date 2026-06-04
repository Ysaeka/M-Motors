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
    /*
   * Dossier completion form
   * Show credit amount only when user has current credit
   */
  const creditRadios = document.querySelectorAll(
    "input[name='has_current_credit']"
  );
  const monthlyCreditWrapper = document.getElementById(
    "monthly-credit-wrapper"
  );

  function toggleMonthlyCreditField() {
    if (!monthlyCreditWrapper || creditRadios.length === 0) {
      return;
    }

    const selectedCreditOption = document.querySelector(
      "input[name='has_current_credit']:checked"
    );

    if (selectedCreditOption && selectedCreditOption.value === "True") {
      monthlyCreditWrapper.classList.remove("d-none");
    } else {
      monthlyCreditWrapper.classList.add("d-none");
    }
  }

  creditRadios.forEach(function (radio) {
    radio.addEventListener("change", toggleMonthlyCreditField);
  });

  toggleMonthlyCreditField();

    /*
   * Dossier completion form
   * Show rent amount only when user is tenant
   */
  const housingStatusSelect = document.getElementById("id_housing_status");
  const monthlyRentWrapper = document.getElementById("monthly-rent-wrapper");

  function toggleMonthlyRentField() {
    if (!housingStatusSelect || !monthlyRentWrapper) {
      return;
    }

    if (housingStatusSelect.value === "tenant") {
      monthlyRentWrapper.classList.remove("d-none");
    } else {
      monthlyRentWrapper.classList.add("d-none");
    }
  }

  if (housingStatusSelect) {
    housingStatusSelect.addEventListener("change", toggleMonthlyRentField);
  }

  toggleMonthlyRentField();
});
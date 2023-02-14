const scannedContainer = document.getElementById("scanned");
const orderedContainer = document.getElementById("ordered");

var currentDataString1 = "";
var currentDataString2 = "";

// function to check for changes in scanned.json
function checkScannedJson() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "../data/scanned.json", true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var resultAsString = xhr.responseText;
      if (!currentDataString1) currentDataString1 = resultAsString;

      if (currentDataString1 !== resultAsString) {
        window.location.reload(1);
      }
      currentDataString1 = resultAsString;
    }
  };
  xhr.send();
}

// function to check for changes in ordered.json
function checkOrderedJson() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "../data/ordered.json", true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var resultAsString = xhr.responseText;
      if (!currentDataString2) currentDataString2 = resultAsString;

      if (currentDataString2 !== resultAsString) {
        window.location.reload(1);
      }
      currentDataString2 = resultAsString;
    }
  };
  xhr.send();
}

// run the functions every 1 seconds
setInterval(checkScannedJson, 1000);
setInterval(checkOrderedJson, 1000);

// Async function to fetch data from the specified URL and return the data in JSON format
async function getData(url) {
  const response = await fetch(url, {
    headers: {
      "Cache-Control": "no-cache, no-store, must-revalidate",
      Pragma: "no-cache",
      Expires: "0",
    },
  });
  const data = await response.json();
  return data;
}

// Async function to create a card with the specified scanned and ordered data
async function createCard(scannedData = {}, orderedData = {}) {
  if (!scannedData && !orderedData) {
    console.error("Both scannedData and orderedData are null");
    return;
  }

  // Create the elements for the card
  const cardWrapper = document.createElement("div");
  cardWrapper.classList.add("card-container");

  const content = document.createElement("div");
  content.classList.add("content");

  const card = document.createElement("div");
  card.classList.add("card");

  const title = document.createElement("h2");
  title.classList.add("title");
  title.textContent = scannedData.itemCode || orderedData.itemCode || "N/A";

  const subtitle = document.createElement("h3");
  subtitle.classList.add("subtitle");
  subtitle.textContent =
    scannedData.description || orderedData.description || "N/A";

  const supplier = document.createElement("p");
  supplier.classList.add("info");
  supplier.textContent = `Supplier: ${
    scannedData.supplier || orderedData.supplier || "N/A"
  }`;

  const orderQuantity = document.createElement("p");
  orderQuantity.classList.add("info");
  orderQuantity.textContent = `Order Quantity: ${
    scannedData.orderQuantity || orderedData.orderQuantity || "N/A"
  }`;

  const scannedDate = document.createElement("p");
  scannedDate.classList.add("info");
  let scannedDateValue = new Date(scannedData.timeStamp || 0);
  scannedDate.textContent = `Scanned Date: ${
    scannedData.timeStamp
      ? scannedDateValue.getFullYear() +
        "-" +
        (scannedDateValue.getMonth() + 1).toString().padStart(2, "0") +
        "-" +
        scannedDateValue.getDate().toString().padStart(2, "0")
      : "N/A"
  }`;

  let orderedDate = null;
  if (orderedData) {
    date = new Date(orderedData.orderDate);
    orderedDate = document.createElement("p");
    orderedDate.classList.add("info");
    orderedDate.textContent = `Ordered Date: ${
      orderedData.orderDate
        ? date.getFullYear() +
          "-" +
          (date.getMonth() + 1).toString().padStart(2, "0") +
          "-" +
          date.getDate().toString().padStart(2, "0")
        : "N/A"
    }`;
  }

  const index = document.createElement("p");
  index.classList.add("index");
  index.textContent =
    scannedData.indexNumber || orderedData.indexNumber || "N/A";

  // Function to set the background color based on the business day difference

  function setBackgroundColor(card, scannedData) {
    const scannedDate = new Date(scannedData.timeStamp || 0);
    const orderedDate = new Date(scannedData.orderDate || 0);
    const today = new Date();
    const daysDiff = Math.floor((today - orderedDate) / (1000 * 60 * 60 * 24));
    if (orderedDate !== null) {
      if (daysDiff >= 4) {
        card.classList.add("red-background");
      } else if (daysDiff > 2 && daysDiff < 4) {
        card.classList.add("yellow-background");
      } else if (daysDiff <= 2) {
        card.classList.add("green-background");
      }
    } else if (scannedDate !== null) {
      const scannedDateDiff = getBusinessDayDifference(scannedDate, today);
      if (scannedDateDiff <= 1) {
        card.classList.add("green-background");
      } else if (scannedDateDiff > 1) {
        card.classList.add("red-background");
      }
    }
  }

  // Determine the difference between the ordered date and the current date
  let orderedDateDiff = null;
  if (orderedData && orderedData.orderDate) {
    orderedDateDiff = getBusinessDayDifference(
      new Date(orderedData.orderDate),
      new Date()
    );
  }

  // Determine the difference between the scanned date and the current date
  let scannedDateDiff = null;
  if (scannedData && scannedData.timeStamp) {
    scannedDateDiff = getBusinessDayDifference(
      new Date(scannedData.timeStamp),
      new Date()
    );
  }

  card.appendChild(content);
  content.appendChild(title);
  content.appendChild(subtitle);
  content.appendChild(supplier);
  content.appendChild(orderQuantity);
  content.appendChild(scannedDate);
  if (orderedDate) {
    content.appendChild(orderedDate);
  }
  content.appendChild(index);

  setBackgroundColor(card, scannedData);

  return card;
}

// Function to calculate the time difference in business days
function getBusinessDayDifference(date1, date2) {
  const oneDay = 24 * 60 * 60 * 1000;
  let diff = Math.abs(date2.getTime() - date1.getTime());
  let businessDays = Math.floor(diff / oneDay);

  // Subtract weekends from the difference
  let start = date1;
  while (start < date2) {
    if (start.getDay() === 0 || start.getDay() === 6) {
      businessDays--;
    }
    start = new Date(start.getTime() + oneDay);
  }
  return businessDays;
}

// Async function to display all the cards
async function displayCards() {
  const scannedData = await getData("./data/scanned.json");
  const orderedData = await getData("./data/ordered.json");

  // added sorting to sort first by vendor, then by itemCode
  orderedData.sort(function (a, b) {
    if (a.supplier < b.supplier) {
      return -1;
    }
    if (a.supplier > b.supplier) {
      return 1;
    }
    if (a.itemCode < b.itemCode) {
      return -1;
    }
    if (a.itemCode > b.itemCode) {
      return 1;
    }
    return 0;
  });

  // added sorting to sort first by vendor, then by itemCode
  scannedData.sort(function (a, b) {
    if (a.supplier < b.supplier) {
      return -1;
    }
    if (a.supplier > b.supplier) {
      return 1;
    }
    if (a.itemCode < b.itemCode) {
      return -1;
    }
    if (a.itemCode > b.itemCode) {
      return 1;
    }
    return 0;
  });

  // Display all items from scanned.json
  for (let i = 0; i < scannedData.length; i++) {
    const createdCard = await createCard(scannedData[i], null);
    scannedContainer.appendChild(createdCard);
  }

  // Display all items from ordered.json
  for (let i = 0; i < orderedData.length; i++) {
    const createdCard = await createCard(orderedData[i], orderedData[i]);
    orderedContainer.appendChild(createdCard);
  }
}

displayCards();

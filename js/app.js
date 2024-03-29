const scannedContainer = document.getElementById("scanned");
const orderedContainer = document.getElementById("ordered");

let currentDataString1 = "";
let currentDataString2 = "";

// function to check for changes in scanned.json
function checkScannedJson() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "../data/scanned.json", true);
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var resultAsString = xhr.responseText;
      if (!currentDataString1) currentDataString1 = resultAsString;

      if (currentDataString1 !== resultAsString) {
        displayCards();
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
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4 && xhr.status === 200) {
      var resultAsString = xhr.responseText;
      if (!currentDataString2) currentDataString2 = resultAsString;

      if (currentDataString2 !== resultAsString) {
        displayCards();
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
  const orderedDate = scannedData.orderDate ? new Date(scannedData.orderDate) : null;
  const today = new Date();

  if (orderedDate !== null) {
    const daysDiff = Math.floor((today - orderedDate) / (1000 * 60 * 60 * 24));

    if (daysDiff <= 1) {
      card.classList.add("green-background");
    } else if (daysDiff >= 2 && daysDiff < 4) {
      card.classList.add("yellow-background");
    } else if (daysDiff >= 4) {
      card.classList.add("red-background");
    }
  } else if (scannedDate !== null) {
    const scannedDateDiff = getBusinessDayDifference(scannedDate, today);

    if (scannedDateDiff <= 1) {
      card.classList.add("green-background");
    } else if (scannedDateDiff > 1 && scannedDateDiff < 4) {
      card.classList.add("yellow-background");
    } else if (scannedDateDiff >= 4) {
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
  
  card.addEventListener("click", function() {
    navigator.clipboard.writeText(title.textContent).then(function() {
      console.log("Copying to clipboard was successful!");
      // Get the overlay and message elements
      var overlay = document.getElementById("overlay");
      var message = document.getElementById("overlayMessage");

      // Set the message text
      message.textContent = "The text " + title.textContent + " was successfully copied to the clipboard";

      // Show the overlay
      overlay.style.display = "flex";

      // Hide the overlay after 1.5 seconds
      setTimeout(function() {
        overlay.style.display = "none";
      }, 1500);
    }, function(err) {
      console.error("Could not copy text: ", err);
    });
  });

  return card;
}

// Function to calculate the time difference in business days
function getBusinessDayDifference(date1, date2) {
  const oneDay = 24 * 60 * 60 * 1000;
  let diff = Math.abs(date2.getTime() - date1.getTime());
  let businessDays = Math.floor(diff / oneDay);

  // Subtract weekends from the difference
  let start = new Date(Math.min(date1.getTime(), date2.getTime()));
  let end = new Date(Math.max(date1.getTime(), date2.getTime()));
  let dayCount = 0;

  while (start <= end) {
    let day = start.getDay();
    if (day !== 0 && day !== 6) {
      dayCount++;
    }
    start.setDate(start.getDate() + 1);
  }

  businessDays -= dayCount;
  return businessDays;
}

// Async function to display all the cards
async function displayCards() {
  scannedContainer.querySelectorAll(".card").forEach((e) => e.remove());
  orderedContainer.querySelectorAll(".card").forEach((e) => e.remove());
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

setTimeout(function () {
  location.reload();
}, 60000);

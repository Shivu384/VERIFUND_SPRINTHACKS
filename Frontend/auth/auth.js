document.getElementById("rs-form").addEventListener("submit", function(event) {
    event.preventDefault();

    const name = document.getElementById("rs-name")?.value?.trim();
    const phone = document.getElementById("rs-phone")?.value?.trim();
    const email = document.getElementById("rs-email")?.value?.trim();
    const password = document.getElementById("rs-password")?.value;

   

    // You can now send this data to a backend API using fetch()
    // Example:
    /*
    fetch('/api/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, phone, email, password })
    })
    .then(res => res.json())
    .then(data => {
      console.log(data);
      // Redirect or show success message
    });
    */
  });
  document.getElementById("lg-loginform").addEventListener("submit", function(event) {
    event.preventDefault();

    const email = document.getElementById("lg-email")?.value?.trim();
    const password = document.getElementById("lg-password")?.value;

    console.log("Email:", email);
    console.log("Password:", password);

    // Example fetch (backend integration)
    /*
    fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    .then(res => res.json())
    .then(data => {
      console.log(data);
      // Redirect or show login success/failure
    });
    */
  });


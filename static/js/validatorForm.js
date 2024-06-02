function validateForm() {
  var price = document.getElementById("price").value;
  if (isNaN(price) || price <= 0) {
    alert("Price must be a positive number");
    return false;
  }
  return true;
}


var myInput = document.getElementById("id_password");
var letter = document.getElementById("letter");
var capital = document.getElementById("capital");
var number = document.getElementById("number");
var length = document.getElementById("length");
var symbol = document.getElementById("symbol");
var repeating = document.getElementById("repeating");
var space = document.getElementById("space");

// When the user clicks on the password field, show the message box
myInput.onfocus = function() {
  document.getElementById("message").style.display = "block";
}

// When the user clicks outside of the password field, hide the message box
myInput.onblur = function() {
  document.getElementById("message").style.display = "none";
}

// When the user starts to type something inside the password field
myInput.onkeyup = function() {
  // Validate lowercase letters
  var lowerCaseLetters = /[a-z]/g;
  if(myInput.value.match(lowerCaseLetters)) {  
    letter.classList.remove("invalid");
    letter.classList.add("valid");
  } else {
    letter.classList.remove("valid");
    letter.classList.add("invalid");
  }
  
  // Validate capital letters
  var upperCaseLetters = /[A-Z]/g;
  if(myInput.value.match(upperCaseLetters)) {  
    capital.classList.remove("invalid");
    capital.classList.add("valid");
  } else {
    capital.classList.remove("valid");
    capital.classList.add("invalid");
  }

  // Validate numbers
  var numbers = /[0-9]/g;
  if(myInput.value.match(numbers)) {  
    number.classList.remove("invalid");
    number.classList.add("valid");
  } else {
    number.classList.remove("valid");
    number.classList.add("invalid");
  }
  
   // Validate symbols
  var symbols = new RegExp("(?=.*[!@#\$%\^&\*])");
  if(myInput.value.match(symbols)) {  
    symbol.classList.remove("invalid");
    symbol.classList.add("valid");
  } else {
    symbol.classList.remove("valid");
    symbol.classList.add("invalid");
  }
  
   // Validate space
  var spaces = /\s/;
  if(myInput.value.match(spaces)) {  
    space.classList.remove("valid");
    space.classList.add("invalid");
  } else {
    space.classList.remove("invalid");
    space.classList.add("valid");
  }
  
    
   // Validate repeating characters

  var repeatings = /(.)\1+/;
  if(myInput.value.match(repeatings)) {  
    repeating.classList.remove("valid");
    repeating.classList.add("invalid");
  } else {
    repeating.classList.remove("invalid");
    repeating.classList.add("valid");
  }
  
  // Validate length
  if(myInput.value.length >= 15) {
    length.classList.remove("invalid");
    length.classList.add("valid");
  } else {
    length.classList.remove("valid");
    length.classList.add("invalid");
  }
}

function viewPassword()
{
  var passwordInput = document.getElementById('id_password');
  var passStatus = document.getElementById('pass-status');

  if (passwordInput.type == 'password'){
    passwordInput.type='text';
    passStatus.className='fa fa-eye-slash';

  }
  else{
    passwordInput.type='password';
    passStatus.className='fa fa-eye';
  }
}

function init_cosy_selectors() {

  csw = document.querySelectorAll('.cosy_selector-select-wrapper');
  var i;

  for (i = 0; i < csw.length; i++) {
    csw[i].addEventListener('click', function() {
    this.querySelector('.cosy_selector-select').classList.toggle('open');
    })
  }

  cso = document.querySelectorAll('.cosy_selector-option');

  for (i = 0; i < cso.length; i++) {
    var option = cso[i];
    input_widget = option.getAttribute('input_widget');
    if (option.hasAttribute("selected")){
      // window.alert(input_widget+":"+option.getAttribute("value"));
      document.querySelector('input[name="'+input_widget+'"]').setAttribute('value', option.getAttribute("value"));
      document.querySelector('.cosy_selector-select__trigger[input_widget="'+input_widget+'"] span').textContent = option.textContent;
    }
    option.addEventListener('click', function() {
          input_widget = this.getAttribute('input_widget');
          // window.alert(input_widget+":"+this.getAttribute("value"));
          document.querySelector('input[name="'+input_widget+'"]').setAttribute('value', this.getAttribute("value"));
          document.querySelector('.cosy_selector-select__trigger[input_widget="'+input_widget+'"] span').textContent = this.textContent;
      })
  }

  window.addEventListener('click', function(e) {
      sct = document.querySelectorAll('.cosy_selector-select');
      for (i = 0; i < sct.length; i++) {
        if (!sct[i].contains(e.target)) {
          sct[i].classList.remove('open');
        }
      }
  });

}

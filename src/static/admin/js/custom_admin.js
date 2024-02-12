document.addEventListener('DOMContentLoaded', function() {
    // Получаем элементы
    var jazzyActions = document.getElementById('jazzy-actions');
    var card = document.querySelector('.card');

    // Перемещаем jazzy-actions над card
    card.parentNode.insertBefore(jazzyActions, card);
    // Изменяем класс col-12 col-lg-9 на col-12 col-lg-12
        var colElement = document.querySelector('.col-12.col-lg-9');
        colElement.classList.remove('col-lg-9');
        colElement.classList.add('col-lg-12');
  });
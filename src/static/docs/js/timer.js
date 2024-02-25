// Получаем элемент div
    var lifeTimeDiv = document.getElementById('life-time');
    // Получаем значения из атрибутов
    var periodeCount = parseInt(lifeTimeDiv.getAttribute('data-periode-count'));
    var periodeAdd = parseInt(lifeTimeDiv.getAttribute('data-periode-add'));
    var periodeTime1 = lifeTimeDiv.getAttribute('data-pause-time-1');
    var periodeTime2 = lifeTimeDiv.getAttribute('data-periode-time-1');
    // Создаем новые значения и добавляем их к элементу
for (var i = 2; i <= periodeCount; i++) {
    // Парсим предыдущее значение времени
    var previousPeriodeTime = lifeTimeDiv.getAttribute('data-pause-time-' + (i - 1)).split(':').map(Number); 
    // Парсим текущее значение времени
    var currentPeriodeTime = periodeTime1.split(':').map(Number);
    // Прибавляем текущее значение к предыдущему значению
    previousPeriodeTime[0] += currentPeriodeTime[0];
    previousPeriodeTime[1] += currentPeriodeTime[1];
    // Форматируем время
    var formattedTime = previousPeriodeTime.map(function (value) {
        return value < 10 ? '0' + value : value;
    }).join(':');
    // Создаем новый атрибут и добавляем его к элементу
    lifeTimeDiv.setAttribute('data-pause-time-' + i, formattedTime); // Change here
}
 // Создаем новые значения и добавляем их к элементу
    for (var i = 2; i <= periodeCount; i++) {
        // Парсим предыдущее значение времени
        var previousPeriodeTime = lifeTimeDiv.getAttribute('data-periode-time-' + (i - 1)).split(':').map(Number);
        // Парсим текущее значение времени
        var currentPeriodeTime = periodeTime2.split(':').map(Number);
        // Прибавляем текущее значение к предыдущему значению
        previousPeriodeTime[0] += currentPeriodeTime[0];
        previousPeriodeTime[1] += currentPeriodeTime[1];
        // Форматируем время
        var formattedTime = previousPeriodeTime.map(function (value) {
            return value < 10 ? '0' + value : value;
        }).join(':');
        // Создаем новый атрибут и добавляем его к элементу
        lifeTimeDiv.setAttribute('data-periode-time-' + i, formattedTime);
    }
// Получаем элемент с id "life-time"
var imgInfoPeriod = document.getElementById("life-time");
// Получаем значения атрибутов
var periodeCount = parseInt(imgInfoPeriod.getAttribute("data-periode-count"));
var pauseTime = parseInt(imgInfoPeriod.getAttribute("data-pause-time-1"));
var periodeTime = parseInt(imgInfoPeriod.getAttribute("data-periode-time-1"));
var startTime = imgInfoPeriod.getAttribute("data-start-time");
// Удаляем существующие атрибуты data-pause-time-start и data-pause-time-end
imgInfoPeriod.removeAttribute("data-pause-time-start");
imgInfoPeriod.removeAttribute("data-pause-time-end");
// Создаем новые атрибуты data-pause-time-start и data-pause-time-end и добавляем их в элемент
for (var i = 1; i <= periodeCount; i++) {
    var pauseTimeEnd = addTimes(startTime, i * (pauseTime + periodeTime));
    var pauseTimeStart = subtractTime(pauseTimeEnd, pauseTime);
    imgInfoPeriod.setAttribute("data-pause-time-start-" + i, pauseTimeStart);
    imgInfoPeriod.setAttribute("data-pause-time-end-" + i, pauseTimeEnd);
}
// Функция для вычитания времени
function subtractTime(startTime, minutesToSubtract) {
    var time = new Date("1970-01-01T" + startTime + "Z");
    time.setMinutes(time.getMinutes() - minutesToSubtract);
    return time.toISOString().substr(11, 8);
}
// Функция для сложения временных значений
function addTimes(startTime, minutesToAdd) {
    var time = new Date("1970-01-01T" + startTime + "Z");
    time.setMinutes(time.getMinutes() + minutesToAdd);
    return time.toISOString().substr(11, 8);
}
//Новый таймер
function updateTimer() {
    var currentTime = document.getElementById("life-time").getAttribute("current-time");
    var startTime = document.getElementById("life-time").getAttribute("data-start-time");
    var pauseStartTimes = [];
    var pauseEndTimes = [];
    var pauseDurations = [];
    // Получите время начала, окончания и продолжительность паузы
    for (var i = 1; i <= 3; i++) {
        var pauseStartTimeAttr = document.getElementById("life-time").getAttribute("data-pause-time-start-" + i);
        var pauseEndTimeAttr = document.getElementById("life-time").getAttribute("data-pause-time-end-" + i);
        if (pauseStartTimeAttr && pauseEndTimeAttr) {
            pauseStartTimes.push(pauseStartTimeAttr);
            pauseEndTimes.push(pauseEndTimeAttr);
            // Рассчитайте продолжительность для каждого периода паузы
            var pauseStart = new Date("2000-01-01 " + pauseStartTimeAttr);
            var pauseEnd = new Date("2000-01-01 " + pauseEndTimeAttr);
            var pauseDuration = (pauseEnd - pauseStart) / 1000; // в секундах
            pauseDurations.push(pauseDuration);
        }
    }
    // Проверьте, находится ли текущее время в пределах диапазона паузы
    for (var i = 0; i < pauseStartTimes.length; i++) {
        if (currentTime >= pauseStartTimes[i] && currentTime <= pauseEndTimes[i]) {
            document.getElementById("life-time").innerText = "перерыв";
            return;
        }
    }
    // Вычислять и отображать затраченное время
    var startDateTime = new Date("2000-01-01 " + startTime);
    var currentDateTime = new Date("2000-01-01 " + currentTime);
    var elapsedMilliseconds = currentDateTime - startDateTime;
    // Вычитайте время, затраченное на паузы
    for (var i = 0; i < pauseStartTimes.length; i++) {
        if (currentTime > pauseEndTimes[i]) {
            elapsedMilliseconds -= pauseDurations[i] * 1000;
        }
    }
    var elapsedSeconds = Math.floor(elapsedMilliseconds / 1000) % 60;
    var elapsedMinutes = Math.floor(elapsedMilliseconds / 60000);
    document.getElementById("life-time").innerText = "" + elapsedMinutes + " : " + elapsedSeconds + "";
}
// Таймер обновления каждую секунду
setInterval(updateTimer, 1000);
// Первоначальное обновление
updateTimer();

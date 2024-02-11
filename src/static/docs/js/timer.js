//Создает нужное количество data-periode-time
var lifeTimeElement = document.getElementById("life-time");
var startTime = lifeTimeElement.getAttribute("data-start-time");
var periodeTime1 = parseInt(lifeTimeElement.getAttribute("data-periode-time-1"), 10);
var pauseTime1 = parseInt(lifeTimeElement.getAttribute("data-pause-time-1"), 10);
var periodeCount = parseInt(lifeTimeElement.getAttribute("data-periode-count"), 10);
for (var i = 2; i <= periodeCount; i++) {
    lifeTimeElement.setAttribute("data-periode-time-" + i, periodeTime1);
    lifeTimeElement.setAttribute("data-pause-time-" + i, pauseTime1);
}
var imgInfo = document.getElementById('life-time');
var startTime = imgInfo.getAttribute('data-start-time');
var periodCount = parseInt(imgInfo.getAttribute('data-periode-count'));
var startDate = new Date('1970-01-01 ' + startTime);
var pauseStartTime = [];
var pauseEndTime = [];
for (var i = 1; i <= periodCount; i++) {
    var periodTime = parseInt(imgInfo.getAttribute('data-periode-time-' + i));
    var pauseTime = parseInt(imgInfo.getAttribute('data-pause-time-' + i));
    var startPause = new Date(startDate.getTime() + periodTime * 1000);
    var endPause = new Date(startPause.getTime() + pauseTime * 1000);
    var startPauseStr = startPause.toTimeString().split(' ')[0];
    var endPauseStr = endPause.toTimeString().split(' ')[0];
    pauseStartTime.push(startPauseStr);
    pauseEndTime.push(endPauseStr);
    startDate = new Date(endPause.getTime() + 1000);
}
for (var i = 0; i < periodCount; i++) {
    imgInfo.setAttribute('data-pause-time-start-' + (i + 1), pauseStartTime[i]);
    imgInfo.setAttribute('data-pause-time-end-' + (i + 1), pauseEndTime[i]);
}
//
// Получить элемент div
// Получить элемент div
var element = document.getElementById("life-time");

// Извлечь значения атрибутов
var startTime = element.getAttribute("data-start-time");
var periodCount = element.getAttribute("data-periode-count");

// Функция для расчета разницы во времени в формате "мм:сс"
function calculateTimeDifference(start, end) {
    var startTime = new Date("1970-01-01 " + start);
    var endTime = new Date("1970-01-01 " + end);
    var difference = new Date(endTime - startTime);
    return (difference.toISOString().substr(14, 5));
}

// Обработка каждого data-pause-time-start
for (var i = 1; i <= periodCount; i++) {
    var pauseTimeStart = element.getAttribute("data-pause-time-start-" + i);
    var pauseTimeEnd = element.getAttribute("data-pause-time-end-" + i);

    var pauseTimeTimer = calculateTimeDifference(pauseTimeEnd, pauseTimeStart);
    element.setAttribute("data-pause-time-timer-" + i, pauseTimeTimer);

    // Обновить startTime для следующего шага
    startTime = pauseTimeEnd;
}


// Получаем элемент с id="life-time"
var lifeTimeElement = document.getElementById("life-time");

// Инициализируем переменную для суммы
var totalPauseTime = 0;

// Перебираем все атрибуты элемента, начинающиеся с "data-pause-time-timer-"
for (var i = 1; ; i++) {
    var attributeName = "data-pause-time-timer-" + i;
    var pauseTimerValue = lifeTimeElement.getAttribute(attributeName);

    // Если атрибут существует, прибавляем его значение к сумме
    if (pauseTimerValue !== null) {
        totalPauseTime += parseInt(pauseTimerValue);

        // Прибавляем значение к следующему атрибуту, если он существует
        var nextAttributeName = "data-pause-time-timer-" + (i + 1);
        var nextPauseTimerValue = lifeTimeElement.getAttribute(nextAttributeName);

        if (nextPauseTimerValue !== null) {
            lifeTimeElement.setAttribute(nextAttributeName, (parseInt(nextPauseTimerValue) + parseInt(pauseTimerValue)).toString());
        } else {
            // Если следующий атрибут не существует, выходим из цикла
            break;
        }
    } else {
        // Если атрибут не существует, выходим из цикла
        break;
    }
}

// Получаем элемент с id="life-time"
var lifeTimeElement = document.getElementById("life-time");

// Инициализируем переменную для суммы
var totalPauseTime = 0;

// Перебираем все атрибуты, начинающиеся с "data-pause-time-timer-"
for (var i = 1; ; i++) {
    var attributeName = "data-pause-time-timer-" + i;
    var pauseTimerValue = lifeTimeElement.getAttribute(attributeName);

    // Если атрибут существует, добавляем его значение к сумме
    if (pauseTimerValue !== null) {
        totalPauseTime += parseInt(pauseTimerValue);
    } else {
        // Если атрибут не существует, выходим из цикла
        break;
    }
}

//Сумирует общее количество времени матча data-periode-end
var periodElement = document.getElementById('life-time');
var periodeTimes = [];
var i = 1;
while (periodElement.hasAttribute('data-periode-time-' + i)) {
    var periodeTime = parseInt(periodElement.getAttribute('data-periode-time-' + i));
    periodeTimes.push(periodeTime);
    i++;
}
var totalPirodeTime = periodeTimes.reduce((acc, time) => acc + time, 0);
var hours = Math.floor(totalPirodeTime / 3600);
var minutes = Math.floor((totalPirodeTime % 3600) / 60);
var seconds = totalPirodeTime % 60;
var formattedResult = hours.toString().padStart(2, '0') + ':' +
    minutes.toString().padStart(2, '0') + ':' +
    seconds.toString().padStart(2, '0');
periodElement.setAttribute('data-periode-end', formattedResult);
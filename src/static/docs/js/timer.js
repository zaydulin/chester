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

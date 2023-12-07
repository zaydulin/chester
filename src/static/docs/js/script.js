const links = document.querySelectorAll('a.nav-link')

links.forEach(link => {
    link.addEventListener('click',
    function () {
        links.forEach(link => {
            link.classList.remove('active')
        })
        this.classList.add('active')

    })
})

function clearContent() {
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        event.detail.target.innerHTML = ''
    });
}

document.body.addEventListener('htmx:afterRequest', function(event) {
    const hxCustom = event.srcElement.getAttribute("hx-custom");
    if (hxCustom === 'title') {
        const dataTitle = document.getElementById("main-content").querySelector("main[data-title]");
        if (dataTitle) {
            textTitle = dataTitle.getAttribute("data-title");
            document.querySelector("head").querySelector("title").innerHTML = textTitle;

            const metaContent = dataTitle.getAttribute("data-content");
            if (metaContent) {
                dataTitle.setAttribute("data-content", metaContent);
            }

            const description = "Your description here"; // Замените эту строку на ваше реальное описание страницы
            dataTitle.setAttribute("data-description", description);
        }
    }
});
const countries = document.querySelectorAll('.events__search-tour + div div');

for (let i = 0; i < countries.length; i++) {
	countries[i].onclick = () => {
		const el = countries[i].nextElementSibling;
		el.classList.toggle('active');
	};
}

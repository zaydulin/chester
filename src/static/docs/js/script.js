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
    if (hxCustom === 'title' || hxCustom === 'description') {
        const dataTitle = document.getElementById("main-content").querySelector("main[data-title]");
        const dataDescription = document.getElementById("main-content").querySelector("main[data-description]");

        if (dataTitle) {
            const textTitle = dataTitle.getAttribute("data-title");
            document.querySelector("head title").innerText = textTitle;
        }

        if (dataDescription) {
            const textDescription = dataDescription.getAttribute("data-description");
            const metaDescription = document.querySelector("head meta[name='description']");
            if (metaDescription) {
                metaDescription.setAttribute("content", textDescription);
            } else {
                const newMeta = document.createElement("meta");
                newMeta.setAttribute("name", "description");
                newMeta.setAttribute("content", textDescription);
                document.querySelector("head").appendChild(newMeta);
            }
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

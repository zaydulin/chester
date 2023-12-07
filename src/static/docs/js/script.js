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
        const textTitle = dataTitle.getAttribute("data-title");
        document.querySelector("head title").innerHTML = textTitle;
      }
    }
    const metaContent = event.srcElement.getAttribute("data-content");
    if (metaContent) {
      document.querySelector("meta[name='description']").setAttribute("content", metaContent);
    }
  });
const countries = document.querySelectorAll('.events__search-tour + div div');

for (let i = 0; i < countries.length; i++) {
	countries[i].onclick = () => {
		const el = countries[i].nextElementSibling;
		el.classList.toggle('active');
	};
}

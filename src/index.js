
const baseAxios = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
})

const handleSearch = ({
  searchInput,
  searchButton,
  content,
  loading,
  endpoint,
}) => {
  const query = searchInput.value;
  searchButton.disabled = true;
  loading = true;
  content.innerHTML = '<div class="spinner-border text-primary mx-auto" role="status">'
  baseAxios.get(endpoint,{
    params:{
      q: query
    }
  }).then((response) => {
      document.title = `Grooble: ${query}`;
      const { data } = response;
      content.innerHTML = '';
      data.forEach((item) => {
        const { title, description, url } = item;
        const card = document.createElement('div');
        card.classList.add('card');
        card.innerHTML = `
          <div class="card-body">
            <h5 class="card-title">${title}</h5>
            <p class="card-text">${description}</p>
          </div>
        `;
        content.appendChild(card);
      });
    })
    .catch((error) => {
      console.log(error);
    })
    .finally(() => {
      searchButton.disabled = false;
      loading = false;
    });
}
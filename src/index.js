
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
  pageData,
  showMoreButton
}) => {
  const query = searchInput.value;
  pageData.page = 1;
  searchButton.disabled = true;
  showMoreButton.style.display = 'none';
  loading = true;
  content.innerHTML = '<div class="spinner-border text-primary mx-auto" role="status">'
  baseAxios.get(endpoint,{
    params:{
      q: query,
      ...pageData
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
      if(data.length === 0){
        content.innerHTML = `
          <div class="alert alert-warning" role="alert">
            No results found
          </div>
        `;
      }
    })
    .catch((error) => {
      console.log(error);
    })
    .finally(() => {
      searchButton.disabled = false;
      showMoreButton.style.display = 'block';
      loading = false;
    });
}

const handleShowMore = ({
  searchInput,
  searchButton,
  content,
  endpoint,
  pageData,
  showMoreButton
}) => {
  const query = searchInput.value;
  searchButton.disabled = true;
  showMoreButton.disabled = true;
  pageData.page += 1;
  baseAxios.get(endpoint,{
    params:{
      q: query,
      ...pageData
    }
  }).then((response) => {
    const { data } = response;
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
  }).catch((error) => {
    console.log(error);
  }).finally(() => {
    searchButton.disabled = false;
    showMoreButton.disabled = false;
  })
}
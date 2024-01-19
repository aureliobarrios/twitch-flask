function filterList() {
    const input = document.getElementById('search').value.toLowerCase();
    const items = document.getElementById('items').getElementsByTagName('option');

    for (let i = 0; i < items.length; i++) {
        const value = items[i].value.toLowerCase();
        if (value.includes(input)) {
            items[i].style.display = 'block';
        } else {
            items[i].style.display = 'none';
        }
    }
}


// When user click analyze button
document.querySelector('.analyze-btn').addEventListener('click', e => {
    document.querySelector('.container').innerHTML = ``;
    document.querySelector('.refresh').innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-refresh-cw"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>'
})

// When user click detail button
document.querySelector('.result-container').addEventListener('click', e => {
    e.preventDefault();
    const btn = e.target.closest('.row');
    const name = btn.dataset.name;
    const date = btn.dataset.date;
    const ceed = btn.dataset.ceed;
    window.location.href = `/detail/?name=${name}&date=${date}&ceed=${ceed}`;
})
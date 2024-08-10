document.addEventListener('DOMContentLoaded', function() {
    var yearSlider = document.createElement('input');
    yearSlider.type = 'range';
    yearSlider.min = '2015';
    yearSlider.max = '2024';
    yearSlider.value = new URLSearchParams(window.location.search).get('year') || '2024';
    yearSlider.step = '1';
    yearSlider.id = 'year-slider';

    var yearValue = document.createElement('span');
    yearValue.id = 'year-value';
    yearValue.textContent = yearSlider.value;

    var sliderContainer = document.createElement('div');
    sliderContainer.style.position = 'absolute';
    sliderContainer.style.top = '50px';
    sliderContainer.style.right = '10px';
    sliderContainer.style.zIndex = '1000';
    sliderContainer.style.backgroundColor = 'white';
    sliderContainer.style.padding = '10px';
    sliderContainer.style.borderRadius = '5px';
    sliderContainer.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';

    sliderContainer.appendChild(yearSlider);
    sliderContainer.appendChild(yearValue);

    var backButton = document.createElement('button');
    backButton.textContent = 'Back';
    backButton.className = 'btn btn-primary btn-sm mt-2';
    backButton.style.marginTop = '10px';

    backButton.addEventListener('click', function() {
        window.location.href = '/';
    });

    sliderContainer.appendChild(backButton);
    document.body.appendChild(sliderContainer);

    yearSlider.addEventListener('input', function() {
        yearValue.textContent = yearSlider.value;
        updateHeatmap(yearSlider.value);
    });

    function updateHeatmap(year) {
        const url = new URL(window.location.href);
        url.searchParams.set('year', year);
        url.searchParams.set('show_heatmap', 'true');
        window.location.href = url.toString();
    }
});

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
    sliderContainer.style.top = '70px';
    sliderContainer.style.right = '50px';  // Adjusted position to ensure visibility
    sliderContainer.style.zIndex = '1000';
    sliderContainer.style.backgroundColor = 'white';
    sliderContainer.style.padding = '15px';
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

    var derivativeButton = document.createElement('button');
    derivativeButton.textContent = isDerivativeMode() ? 'Toggle Normal Mode' : 'Toggle Derivative Mode';
    derivativeButton.className = 'btn btn-secondary btn-sm mt-2';
    derivativeButton.style.marginTop = '10px';

    derivativeButton.addEventListener('click', function() {
        toggleDerivativeMode(yearSlider.value);
    });

    // Scale up the slider and buttons
    sliderContainer.style.transform = 'scale(1.3)';  // Scale up the entire container
    yearSlider.style.width = '200px';  // Ensure the slider has enough width

    sliderContainer.appendChild(derivativeButton);
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

    function toggleDerivativeMode(year) {
        const url = new URL(window.location.href);
        if (isDerivativeMode()) {
            url.pathname = '/heatmap';
            derivativeButton.textContent = 'Toggle Derivative Mode';
        } else {
            url.pathname = '/heatmap_derivative_plot';
            derivativeButton.textContent = 'Toggle Normal Mode';
        }
        url.searchParams.set('year', year);
        url.searchParams.set('show_heatmap', 'true');
        window.location.href = url.toString();
    }

    function isDerivativeMode() {
        return window.location.pathname.includes('derivative');
    }
});

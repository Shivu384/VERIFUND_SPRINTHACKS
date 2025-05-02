// Toggle Modal
function toggleModal() {
    document.getElementById('offerModal').classList.toggle('hidden');
}

// Initialize Charts
const returnsCtx = document.getElementById('returnsChart').getContext('2d');
let returnsChartInstance = new Chart(returnsCtx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
            label: 'Monthly Returns',
            data: [12, 19, 3, 5, 2, 3],
            borderColor: '#3B82F6',
            borderWidth: 2,
            tension: 0.4,
            fill: false
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    borderDash: [2, 2],
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        },
        plugins: {
            legend: {
                display: false,
            },
        }
    }
});

const riskCtx = document.getElementById('riskChart').getContext('2d');
let riskChartInstance = new Chart(riskCtx, {
    type: 'doughnut',
    data: {
        labels: ['Low Risk', 'Medium Risk', 'High Risk'],
        datasets: [{
            data: [60, 30, 10],
            backgroundColor: ['#22C55E', '#FACC15', '#EF4444'],
            borderWidth: 0,
            hoverOffset: 4
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                }
            },
        }
    }
});

function resizeCharts() {
    returnsChartInstance.resize();
    riskChartInstance.resize();
}

window.addEventListener('resize', resizeCharts);


// Form Handling
document.getElementById('offerForm').addEventListener('submit', (e) => {
    e.preventDefault();
    toggleModal();            
    const amount = document.getElementById('amount').value;
    const interest = document.getElementById('interest').value;
    const duration = document.getElementById('duration').value;
    console.log('New Offer:', { amount, interest, duration });            
});
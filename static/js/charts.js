document.addEventListener("DOMContentLoaded", function () {
    if (typeof trafficData !== 'undefined') {
        const ctx = document.getElementById('trafficChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: trafficData.labels,
                datasets: [
                    {
                        label: 'Sessions',
                        data: trafficData.sessions,
                        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--primary').trim() || '#1D4ED8',
                        tension: 0.1,
                        fill: false
                    },
                    {
                        label: 'Users',
                        data: trafficData.users,
                        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#065F46',
                        tension: 0.1,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    if (typeof sourceData !== 'undefined') {
        const ctx2 = document.getElementById('sourceChart').getContext('2d');
        new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: sourceData.labels,
                datasets: [{
                    data: sourceData.values,
                    backgroundColor: [
                        getComputedStyle(document.documentElement).getPropertyValue('--primary').trim() || '#1D4ED8',
                        getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#065F46',
                        '#F59E0B', '#3B82F6', '#10B981'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
});

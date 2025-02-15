document.addEventListener('DOMContentLoaded', function () {
    // Récupérer les données du graphique en camembert
    const sentimentElement = document.getElementById('sentimentData');
    if (!sentimentElement) {
        console.error("Élément #sentimentData introuvable !");
        return;
    }

    const sentimentData = {
        positif: parseInt(sentimentElement.getAttribute('data-positif')),
        neutre: parseInt(sentimentElement.getAttribute('data-neutre')),
        negatif: parseInt(sentimentElement.getAttribute('data-negatif'))
    };

    // Récupérer les données du graphique en ligne
    const trendElement = document.getElementById('trendData');
    if (!trendElement) {
        console.error("Élément #trendData introuvable !");
        return;
    }

    const trendData = {
        labels: JSON.parse(trendElement.getAttribute('data-labels')),
        scores: JSON.parse(trendElement.getAttribute('data-scores'))
    };

    // Graphique en camembert (répartition des sentiments)
    const ctx1 = document.getElementById('sentimentChart').getContext('2d');
    new Chart(ctx1, {
        type: 'pie',
        data: {
            labels: ['Positif', 'Neutre', 'Négatif'],
            datasets: [{
                data: [sentimentData.positif, sentimentData.neutre, sentimentData.negatif],
                backgroundColor: ['#4CAF50', '#FFEB3B', '#F44336']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Répartition des Sentiments'
                }
            }
        }
    });

    // Graphique en ligne (évolution des sentiments)
    const ctx2 = document.getElementById('trendChart').getContext('2d');
    new Chart(ctx2, {
        type: 'line',
        data: {
            labels: trendData.labels,
            datasets: [
                {
                    label: 'Positif',
                    data: trendData.scores.map(score => score === 1 ? 1 : 0),
                    borderColor: '#4CAF50',
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'Neutre',
                    data: trendData.scores.map(score => score === 0 ? 1 : 0),
                    borderColor: '#FFEB3B',
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'Négatif',
                    data: trendData.scores.map(score => score === -1 ? 1 : 0),
                    borderColor: '#F44336',
                    tension: 0.1,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Évolution des Sentiments'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Dates'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Score de Sentiment'
                    },
                    min: 0,
                    max: 1
                }
            }
        }
    });
});

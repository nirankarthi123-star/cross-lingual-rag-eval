const API_BASE = 'http://localhost:8000'; // Assume backend runs on 8000
let rawResults = [];

// Format helpers
const formatCondition = (lang, mit) => {
    let l = lang === 'english' ? 'English' : 
            lang === 'tamil_english' ? 'Tamil-English' : 'Hindi-English';
    return `${l} (${mit ? 'Mitigated' : 'Baseline'})`;
};

// Initialize Dashboard
async function init() {
    try {
        const [summaryRes, resultsRes] = await Promise.all([
            fetch(`${API_BASE}/api/dashboard/summary`),
            fetch(`${API_BASE}/api/dashboard/results`)
        ]);

        const summaryData = await summaryRes.json();
        const resultsData = await resultsRes.json();

        document.getElementById('loading').classList.add('hidden');

        if (summaryData.status === 'empty' || !resultsData.results || resultsData.results.length === 0) {
            document.getElementById('empty-state').classList.remove('hidden');
            return;
        }

        document.getElementById('dashboard').classList.remove('hidden');
        rawResults = resultsData.results;

        renderOverview(summaryData.overview);
        renderSuccessCriterion(summaryData.success_criterion);
        renderCharts(summaryData.condition_summaries);
        
        setupFilters();
        renderTable(rawResults);

    } catch (e) {
        console.error(e);
        document.getElementById('loading').innerHTML = `<p style="color:red">Error loading data. Is the backend running?</p>`;
    }
}

function renderOverview(data) {
    document.getElementById('metric-queries').textContent = data.total_queries_evaluated;
    document.getElementById('metric-experiments').textContent = data.total_experiments;
    document.getElementById('metric-faithfulness').textContent = data.average_faithfulness.toFixed(3);
    document.getElementById('metric-hallucination').textContent = (data.overall_hallucination_rate * 100).toFixed(1) + '%';
}

function renderSuccessCriterion(criteria) {
    const container = document.getElementById('success-criterion-container');
    container.innerHTML = '';
    
    criteria.forEach(c => {
        let badgeClass = c.decision === 'MET' ? 'met' : c.decision === 'NOT MET' ? 'not-met' : 'insufficient';
        const html = `
            <div class="card">
                <h3>${c.comparison.replace(' versus ', ' vs ')}</h3>
                <p style="margin-bottom: 10px;">
                    Eng Base: <strong>${c.english_baseline_mean || 'N/A'}</strong><br>
                    Mitigated: <strong>${c.mitigated_mean || 'N/A'}</strong><br>
                    Diff: <strong>${c.difference !== null ? c.difference : 'N/A'}</strong>
                </p>
                <span class="badge ${badgeClass}">${c.decision}</span>
            </div>
        `;
        container.innerHTML += html;
    });
}

function renderCharts(summaries) {
    const conds = ['english', 'tamil_english', 'hindi_english'];
    const labels = ['English', 'Tamil-English', 'Hindi-English'];
    
    // 1. Language Comparison (Baseline Faithfulness)
    const baseFaith = conds.map(c => summaries[`${c}_baseline`]?.mean || 0);
    new Chart(document.getElementById('chart-language'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Baseline Faithfulness',
                data: baseFaith,
                backgroundColor: '#2563eb'
            }]
        },
        options: { scales: { y: { min: 0, max: 1 } } }
    });

    // 2. Baseline vs Mitigation
    const mitFaith = conds.map(c => summaries[`${c}_mitigated`]?.mean || 0);
    new Chart(document.getElementById('chart-mitigation'), {
        type: 'bar',
        data: {
            labels: ['Tamil-English', 'Hindi-English'],
            datasets: [
                {
                    label: 'Baseline',
                    data: [baseFaith[1], baseFaith[2]],
                    backgroundColor: '#94a3b8'
                },
                {
                    label: 'Mitigated',
                    data: [mitFaith[1], mitFaith[2]],
                    backgroundColor: '#16a34a'
                }
            ]
        },
        options: { scales: { y: { min: 0, max: 1 } } }
    });

    // 3. Hallucination Rates
    const baseHal = conds.map(c => summaries[`${c}_baseline`]?.hallucination_rate || 0);
    const mitHal = conds.map(c => summaries[`${c}_mitigated`]?.hallucination_rate || 0);
    new Chart(document.getElementById('chart-hallucination'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Baseline Rate',
                    data: baseHal,
                    backgroundColor: '#f87171'
                },
                {
                    label: 'Mitigated Rate',
                    data: mitHal,
                    backgroundColor: '#ef4444'
                }
            ]
        },
        options: { scales: { y: { min: 0, max: 1 } } }
    });
}

// Table & Filtering
function setupFilters() {
    const filters = ['filter-language', 'filter-mitigation', 'filter-hallucination'];
    filters.forEach(id => {
        document.getElementById(id).addEventListener('change', () => {
            const lang = document.getElementById('filter-language').value;
            const mit = document.getElementById('filter-mitigation').value;
            const hal = document.getElementById('filter-hallucination').value;
            
            let filtered = rawResults.filter(r => {
                if (lang && r.language !== lang) return false;
                if (mit && String(r.mitigation_enabled) !== mit) return false;
                if (hal && String(r.hallucination_flag) !== hal) return false;
                return true;
            });
            renderTable(filtered);
        });
    });
}

function renderTable(data) {
    const tbody = document.getElementById('results-tbody');
    tbody.innerHTML = '';
    
    data.forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${r.question_id}</td>
            <td>${r.language}</td>
            <td>${r.mitigation_enabled ? 'ON' : 'OFF'}</td>
            <td>${r.faithfulness_score.toFixed(3)}</td>
            <td>
                <span class="badge ${r.hallucination_flag ? 'not-met' : 'met'}">
                    ${r.hallucination_flag ? 'TRUE' : 'FALSE'}
                </span>
            </td>
            <td>${r.generator_model || 'Unknown'}</td>
            <td><button class="view-btn" onclick='openModal(${JSON.stringify(r).replace(/'/g, "&apos;")})'>View</button></td>
        `;
        tbody.appendChild(tr);
    });
}

// Modal Logic
function openModal(r) {
    document.getElementById('modal-qid').textContent = r.question_id;
    document.getElementById('modal-lang').textContent = r.language;
    document.getElementById('modal-mit').textContent = r.mitigation_enabled ? 'ON' : 'OFF';
    document.getElementById('modal-faith').textContent = r.faithfulness_score.toFixed(3);
    document.getElementById('modal-hal').textContent = r.hallucination_flag ? 'TRUE' : 'FALSE';
    
    document.getElementById('modal-orig-query').textContent = r.original_query;
    document.getElementById('modal-norm-query').textContent = r.normalized_query || '(None)';
    document.getElementById('modal-context').textContent = r.retrieved_context;
    document.getElementById('modal-answer').textContent = r.generated_answer;
    document.getElementById('modal-explanation').textContent = r.judge_explanation || '(None)';
    
    document.getElementById('explorer-modal').classList.remove('hidden');
}

document.getElementById('modal-close').addEventListener('click', () => {
    document.getElementById('explorer-modal').classList.add('hidden');
});

// Run
window.addEventListener('DOMContentLoaded', init);
